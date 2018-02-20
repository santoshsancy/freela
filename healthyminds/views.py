import logging
import json

from itertools import chain
from datetime import date, datetime, timedelta, time

from django.contrib import messages
from django.contrib.auth import (get_user_model, get_user, authenticate,
                                 login as auth_login, logout as auth_logout,)

from django.core.urlresolvers import reverse_lazy, resolve, reverse

from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, View
from django.http import (HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404, JsonResponse)
from django.shortcuts import redirect, render, render_to_response, get_object_or_404

from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from console.decorators import login_required, staff_required

from healthyminds.codelibrary import (CreateObjectView, UpdateOrDeleteView, ObjectListView,
                                    SingleObjectMixin, JSONResponseMixin, JSONResponseView, RedirectMixin)

from tracking.models import Event
from tracking.utils import create_event, UserLogPageViewMixin
from tracking.views import RecordEventView

logger = logging.getLogger(__name__)

class RouterView(View):
    login_url = 'welcome'
    redirect_pattern = 'homepage'
    staff_redirect_pattern = None

    def get(self, request, *args, **kwargs):
        return redirect(self.get_redirect_url())

    def get_access_url(self):
        ACCESS_CHECKS = (
                         (self.request.user,'setup_completed', reverse_lazy('homepage')),
                         )
        for obj, lock, url in ACCESS_CHECKS:
            if not getattr(obj, lock):
                return redirect(url)

    def get_redirect_url(self):
        if not self.request.user.is_authenticated():
            return reverse_lazy(self.login_url)
        elif self.staff_redirect_pattern and self.request.user.staff_access:
            return reverse_lazy(self.staff_redirect_pattern)
        return reverse_lazy(self.redirect_pattern)

where_to_go = never_cache(RouterView.as_view())

class HomepageView(UserLogPageViewMixin, TemplateView):
    template_name = 'healthyminds/homepage.html'

homepage = login_required(HomepageView.as_view())

class HealthyMindsLoginView(TemplateView):
    template_name = 'healthyminds/welcome.html'

    def get_context_data(self, **kwargs):
        context = super(HealthyMindsLoginView, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form_name = 'login_form'
        context[form_name]=context[form_name](data=request.POST, files=request.FILES)

        if context[form_name].is_valid():
            auth_login(request, context[form_name].get_user())
            return redirect(reverse_lazy('where'), permanent=True)
        return self.render_to_response(context)

login_page = never_cache(HealthyMindsLoginView.as_view())
