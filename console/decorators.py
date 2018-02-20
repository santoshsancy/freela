from django.utils.functional import wraps
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse, reverse_lazy

def staff_required(function=None, login_url='where', redirect_field_name="/"):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and (u.is_staff or u.is_superuser),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def superuser_required(function=None, login_url='where', redirect_field_name="/"):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def login_required(function=None, login_url="where", redirect_field_name="/"):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def debug_access(function=None, login_url='where', redirect_field_name="/"):
    actual_decorator = user_passes_test(
        lambda u: settings.DEBUG,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
