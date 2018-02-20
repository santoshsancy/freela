import uuid, json, random, unicodedata, time
import re, os, sys, traceback, operator
import logging
import unicodecsv as csv

from random import choice, randint
from datetime import datetime, timedelta

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.template import Context, loader
from django.template.response import TemplateResponse
from django.template.context import RequestContext
from django.shortcuts import redirect, render_to_response, get_object_or_404, resolve_url

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.views import login as login_view, logout_then_login
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator

from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm

from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import reverse_lazy, resolve, reverse
from django.utils.http import is_safe_url, urlsafe_base64_decode

from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory

from django.views.generic import TemplateView, FormView, View
from django.views.decorators.cache import never_cache

from django.db.models import F, Q
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.conf import settings

from healthyminds.codelibrary import (CreateObjectView, UpdateObjectView, ObjectListView,
    UpdateOrDeleteView, SingleObjectMixin, RedirectMixin, ModalFormMixin, ModelFormsetMixin, JSONResponseView)

from console.decorators import staff_required, superuser_required, login_required
from console.forms import (UserCreationForm, StaffCreationForm, StaffInitForm,
   StaffAccountModificationForm, AccountModificationForm)

from tracking.models import Event
from tracking.utils import create_event, UserLogPageViewMixin, user_log_page_view
from tracking.views import RecordEventView

logger = logging.getLogger(__name__)

@never_cache
def custom_login(request, **kwargs):
    if request.user.is_authenticated():
        return redirect('where', permanent=True)
    return login_view(request, **kwargs)

class DashboardView(TemplateView):
    template_name = 'console/console-overview.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        return context

dashboard = staff_required(DashboardView.as_view())

class AccountCreationView(TemplateView):
    template_name = 'console/account/account_setup.html'
    form_class = UserCreationForm
    redirect_pattern = 'user-management'

    subject_template_name = "console/account/account_password_subject.txt"
    email_template_name = "console/account/account_password.html"

    def get(self, request, *args, **kwargs):
        self.user_form = self.form_class()
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(AccountCreationView, self).get_context_data(**kwargs)
        context['form'] = self.user_form
        context['obj_name']= 'Account'
        context['cancel_url'] = self.get_redirect_url()
        return context

    def get_redirect_url(self):
        return reverse_lazy(self.redirect_pattern)

    def post(self, request, *args, **kwargs):
        self.user_form = self.form_class(request.POST)
        if self.user_form.is_valid():
            user = self.user_form.save()
            setpsw=PasswordResetForm(data={'email':user.email})
            if setpsw.is_valid():
                setpsw.save(subject_template_name=self.subject_template_name,
                             email_template_name=self.email_template_name)
                messages.success(request, "Invitation email sent to %s" % user.email)
            return self.get_redirect_url()
        return self.render_to_response(self.get_context_data())

account_creation = staff_required(AccountCreationView.as_view())

class StaffCreationView(AccountCreationView):
    template_name = 'console/account/staff-account-setup.html'

    def get(self, request, *args, **kwargs):
        self.user_form =  StaffInitForm()
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.user_form =  StaffInitForm(request.POST)
        if self.user_form.is_valid():
            user = self.user_form.save(commit=False)
            user.is_staff=True
            user.save()
            setpsw=PasswordResetForm(data={'email':user.email})
            if setpsw.is_valid():
                setpsw.save(subject_template_name=self.subject_template_name,
                            email_template_name=self.email_template_name)
                messages.success(request, "Invitation email sent to %s" % user.email)
            return redirect(self.get_redirect_url())
        return self.render_to_response(self.get_context_data())

staff_creation = staff_required(StaffCreationView.as_view())

class UserManagementView(ObjectListView):
    template_name = 'console/management/user-management.html'
    model = get_user_model()
    edit_pattern = 'staff-modify-account'

user_management = staff_required(UserManagementView.as_view())

class UserSearchListView(UserManagementView):

    def get_searchtext(self):
        return self.request.GET.get('search','')

    def get_filter(self):
        return self.request.GET.get('filter')

    def get_objectlist(self):
        return self.search_queryset(searchtext=self.get_searchtext(), filter=self.get_filter())

    def get_queryset(self, filter=None):
        pass

    def search_queryset(self, searchtext, **kwargs):
        pass

class ManagementUserListView(UserSearchListView):
    template_name = 'console/management/userlist.html'

    ADMIN_FILTER = 'admin'
    ALL_FILTER = 'all'
    FILTER_OPTIONS = [ADMIN_FILTER, ALL_FILTER]

    def get_queryset(self, filter=None):
        if filter and filter == self.ADMIN_FILTER:
            return self.model.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
        return self.model.objects.all()

    def search_queryset(self, searchtext, **kwargs):
        qs = self.get_queryset(**kwargs)
        for text in searchtext.split():
            qs = qs.filter(Q(first_name__icontains = text) | Q(last_name__icontains = text) |
                           Q(username__icontains = text) | Q(email__icontains = text))
        return qs

    def get_page_number(self):
        return self.request.GET.get('page', '1')

    def get_item_number(self):
        return self.request.GET.get('pageitems', '1')

    def get_page_list(self):
        paginator = Paginator(self.get_objectlist(), self.get_item_number())
        try:
            page_object_list = paginator.page(self.get_page_number())
        except PageNotAnInteger:
            page_object_list = paginator.page(1)
        except EmptyPage:
            page_object_list = paginator.page(paginator.num_pages)
        return page_object_list

    def get_context_data(self, **kwargs):
        context = super(ManagementUserListView, self).get_context_data(**kwargs)
        context['object_list'] = self.get_page_list()
        context['page_number'] = self.get_page_list().number
        context['max_pages'] = self.get_page_list().paginator.num_pages
        return context

management_userlist = staff_required(ManagementUserListView.as_view())

class ModifyMyAccountView(UpdateOrDeleteView):
    template_name = 'console/management/edit-user.html'
    model = get_user_model()
    form = AccountModificationForm
    redirect_pattern = "where"

    def get(self, request, *args, **kwargs):
        return super(ModifyMyAccountView, self).get(request,
            obj_id=self.request.user.id, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(ModifyMyAccountView, self).post(request,
            obj_id=self.request.user.id, *args, **kwargs)

    def get_form_params(self):
        return {
            'user': self.request.user.id,
            'auth_backend': self.request.session['_auth_user_backend']
        }

modify_my_account = login_required(ModifyMyAccountView.as_view())

class ModifyAccount(UpdateOrDeleteView):
    template_name = 'console/management/edit-user.html'
    model = get_user_model()
    form = StaffAccountModificationForm
    delete_permission = 'is_superuser'
    redirect_pattern = "user-management"

modify_account = staff_required(ModifyAccount.as_view())

@superuser_required
def csv_dump(request, filename="test"):
    csv_filename = '%s.csv' % filename.rstrip('/')
    csvfile_FILE_PATH = os.path.join(settings.PROJECT_ROOT + "/csv_files", csv_filename)

    try:
        with open(csvfile_FILE_PATH, 'rb') as csvfile:
            response = HttpResponse(mimetype='text/csv')
            response['Content-Disposition'] = 'attachment; filename=%s.csv' % filename
            writer = csv.writer(response)
            csvreader = csv.reader(csvfile, delimiter=",")
            for row in csvreader:
                writer.writerow(row)
            return response
    except IOError as e:
        return HttpResponse("File does not exist.")

@staff_required
def generate_csv(request):
    filename=request.GET.get('filename')
    return HttpResponse('wait')

@never_cache
@staff_required
def csv_file_ready(request, filename="test"):
    data, created = DataFiles.objects.get_or_create(name=filename.rstrip('/'))
    if data.generated:
        return HttpResponse(data.result)
    return HttpResponse('generating')

"""Stack traceback function"""
def formatExceptionInfo(maxTBlevel=8):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    return (excName, excArgs, excTb)

def presentExceptionOutput(maxTBlevel=8):
    excName, excArgs, excTb = formatExceptionInfo(maxTBlevel)
    output = "Exception Name:%s\nException Args: %s \n\n%s" % (excName, excArgs, "\n".join(excTb))

# ParaData - Views
class EventDataExporter(object):
    index = ['user_id','name','timestamp','note']

    def __init__(self):
        self.directory = os.path.join(settings.PROJECT_ROOT + "/csv_files/")
        self.events = Event.objects.filter(user__is_staff=False).order_by('timestamp').values(*self.index)

    def write_output(self):
        with open(self.directory+"EventData.csv", 'wb') as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=self.index)
            writer.writeheader()
            for event in self.events:
                try:
                    writer.writerow(event)
                except Exception as e:
                    for key, val in event.items():
                        event[key] = unicode(val).encode('utf-8',errors="ignore")
                        writer.writerow(event)
            csvfile.close()

def export_eventdata():
    EventDataExporter().write_output()

class EmailManager(object):
    email_template = 'emailreminders/reminder_email.txt'

    def __init__(self, user, **kwargs):
        self.send_email(user, **kwargs)

    def validateEmail(self, email ):
        try: validate_email( email )
        except ValidationError:
            return False
        return True

    def send_email(self, user, subject, body, domain_override=None, use_https=False, from_email=None, **kwargs):
        if not domain_override:
            current_site = Site.objects.get_current()
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        t = loader.get_template(self.email_template)
        c = {'email': user.email,'domain': domain,'site_name':
             site_name,'user_id': int_to_base36(user.id),'user': user,
             'protocol': use_https and 'https' or 'http','section': 'Body_%s' % section}
        msg = EmailMessage(_("%s") % (subject), body, from_email, [user.email])
        msg.content_subtype = "html"
        msg.send()
        create_event(name="Email reminder for %s " % section, user=user, note="Email %s" % user.email)

def record_event(request):
    type=request.GET.get('type')
    note=request.GET.get('note','')
    if type:
        create_event(name=type,request=request,user=request.user,note=note)
        status={'saved':'success'}
    else: status={'saved':'failure'}
    return HttpResponse(json.dumps(status), mimetype='application/json')
