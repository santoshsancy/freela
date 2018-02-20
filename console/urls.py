from django.conf.urls import include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import RedirectView
from django.contrib.auth import views as auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.views.generic import TemplateView
from console.forms import ParticipantCreationForm, AccountModificationForm
from console.decorators import staff_required
from console import views as console

#### Password URLS ####
password_patterns = [
    url(r'^password-reset/$', auth.password_reset, {
        'template_name': 'console/account/password_reset.html',
        'email_template_name': 'console/account/password_reset.txt',
        'post_reset_redirect': reverse_lazy('console-password-reset-sent'),
        }, name="console-password-reset"),
    url(r'^password-reset-confirm/(?P<uidb64>\w*)\|(?P<token>[\-a-zA-Z0-9]*)$', auth.password_reset_confirm, {
        'template_name': 'console/account/password_reset_confirm.html',
        'post_reset_redirect': reverse_lazy('console-password-reset-complete'),
        }, name="console-password-reset-confirm"),
    url(r'^password-reset-sent/$', auth.password_reset_done, {
        'template_name': 'console/account/password_reset_sent.html',
        }, name="console-password-reset-sent"),
    url(r'^password-reset-complete/$', auth.password_reset_complete, {
        'template_name': 'console/account/password_reset_complete.html',
        }, name="console-password-reset-complete"),
    url(r'^account-confirm-retry/$', auth.password_reset, {
        'template_name': 'console/account/password_reset.html',
        'email_template_name': 'console/account/account_password.html',
        'post_reset_redirect': reverse_lazy('console-password-reset-sent'),
        }, name="account-confirm-retry"),
]

#### Console URLS ####
console_patterns = [
    url(r'^UserManagement/$', console.user_management, name="user-management"),
    url(r'^AccountCreation/', console.account_creation, name="account-creation"),
    url(r'^account-confirm/(?P<uidb64>\w*)\|(?P<token>[\-a-zA-Z0-9]*)$', auth.password_reset_confirm,
        {'template_name': 'console/account/password_reset_confirm.html', 'set_password_form':ParticipantCreationForm,
         'post_reset_redirect': reverse_lazy('console-password-reset-complete'),
        }, name="console-account-confirm"),

    url(r'^ParticipantAccount/$', console.account_creation, name='new-participant' ),
    url(r'^StaffAccount/$', console.staff_creation, name='new-staff' ),
    url(r'^ModifyAccount/(?P<obj_id>.+?)/$', console.modify_account, name='staff-modify-account'),
    url(r'^ModifyMyAccount/$', console.modify_my_account, name='user-modify-account'),
]

#### Utility URLS ####
utility_patterns = [
    url(r'^logout/$', console.logout_then_login, {'login_url':reverse_lazy('where')}, name='console-logout'),
    url(r'^$', RedirectView.as_view(url=reverse_lazy('console-login')),  name='console-root'),
    url(r'^RecordEvent/$', console.record_event, name="record-event"),

    url(r'^generate_csv/$', console.generate_csv, name='csv-create'),
    url(r'^csv_downloading/(?P<filename>.+?)$', console.csv_dump, name='csv-dump'),
    url(r'^csv-file-ready/(?P<filename>.+?)$', console.csv_file_ready, name='csv-file-ready'),

    url(r'^ajax-userlist/$', console.management_userlist, name="management-userlist"),
]

urlpatterns = (password_patterns + console_patterns + utility_patterns)
