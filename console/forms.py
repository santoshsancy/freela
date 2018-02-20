import re
import random
import bleach
import logging

from datetime import date, datetime

from itertools import chain

from django import forms
from django.forms.formsets import DELETION_FIELD_NAME
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django_localflavor_us import forms as usforms, us_states

from healthyminds.codelibrary import (CompletionDateField)
from healthyminds.models import Institution

from ckeditor.widgets import CKEditorWidget

logger = logging.getLogger(__name__)

class BleachMixin(object):
    allowed_tags = ['strong', 'u', 'em', 'b', 'i',
                    'ul', 'ol', 'li', 'a', 'img',
                    'span', 'code', 'pre', 'sub', 'sup', 'p']

    allowed_attr = ['target', 'href', 'src', 'class']

    def bleach_data(self, data):
        return bleach.clean(data, tags=self.allowed_tags,
            attributes=self.allowed_attr, strip=True)


class ParticipantAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_("E-mail/Username"), max_length=254)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'] % {
                        'username': self.username_field.verbose_name
                    })
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

class UserCreationForm(forms.ModelForm):
    """A form that creates a user, with no privileges, from the given username and password."""

    email = forms.EmailField(label=_("E-mail address"), required=False, max_length=75)

    error_messages = {
        'invalid': _("You must enter a valid email address."),
        }

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name",'email',)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email is not None and email != '':
            try:
                get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                return email
            if email == self.instance.email:
                return email
            raise forms.ValidationError(_("The email address provided is already registered."))
        return email

    def clean(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get("username")
        if not username and not email:
            raise forms.ValidationError(self.error_messages['invalid'])
        return self.cleaned_data

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(get_user_model().objects.make_random_password())
        if user.username in [None,'']:
            user.username = user.email
        if commit:
            user.save()
        return user

class AccountModificationForm(forms.ModelForm):
    error_messages = {
        'invalid': _("You must enter a valid email address."),
        }

    def __init__(self, user=None, auth_backend=None, *args, **kwargs):
        self.user = user
        self.auth_backend = auth_backend

        super(AccountModificationForm, self).__init__(*args, **kwargs)

        if self.email_required():
            self.fields['email'] = forms.EmailField(label=_("E-mail address"), required=True, max_length=75)
            self.fields['email'].initial = AccountModificationForm._meta.model.objects.get(pk=self.user).email

    def email_required(self):
        return True if 'EmailOrUsernameBackend' in self.auth_backend else False

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name")

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            return username
        if username == self.instance.username:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email is not None and email != '':
            try:
                get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                return email
            if email == self.instance.email:
                return email
            raise forms.ValidationError(_("The email address provided is already registered."))
        return email

    def clean(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get("username")
        if not username and not email and self.email_required():
            raise forms.ValidationError(self.error_messages['invalid'])
        return self.cleaned_data

class StaffAccountModificationForm(AccountModificationForm):

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name",'email', 'is_active', 'is_staff']

class ParticipantCreationForm(UserCreationForm):
    email = forms.EmailField(label=_("E-mail address"), required=True, max_length=75)
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ParticipantCreationForm, self).__init__(instance = self.user, *args, **kwargs)

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name",'email',"password1","password2")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email is not None and email != '':
            try:
                u=get_user_model().objects.get(email=email)
                if u.id == self.instance.id:
                    return email
            except get_user_model().DoesNotExist:
                return email
            raise forms.ValidationError(_("The email address provided is already registered."))
        return email

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if user.username in [None,'']:
            user.username = user.email
        if commit:
            user.setup_completed=datetime.now()
            user.save()
        return user

class StaffInitForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name",'email')

class StaffCreationForm(UserCreationForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."))

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        user = super(StaffCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if user.username in [None,'']:
            user.username = user.email
        if commit:
            user.setup_completed=datetime.datetime.now()
            user.is_staff=True
            user.save()
        return user

class CSVForm(forms.Form):
    upload_CSV_file = forms.FileField(
        label='Import CSV File',
        widget=forms.FileInput(attrs={'accept':'text/csv'})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CSVForm, self).__init__(*args, **kwargs)

    def clean(self):
        CSV_MINIMUM_ROW_LENGTH = 8
        MIN_CSV_FILE_SIZE_B = 100
        MAX_CSV_FILE_SIZE_B = 10 * (1024 * 1024)

        csv_file = self.cleaned_data.get('upload_CSV_file')

        # Validate size (type / extension is already enforced by widget)
        if csv_file.size > MAX_CSV_FILE_SIZE_B or csv_file.size < MIN_CSV_FILE_SIZE_B:
            raise forms.ValidationError('Invalid file size (10MB max) or truncated file')

        # Ensure first row has the correct number of fields
        if len(str(csv_file.readline()).split(',')) < CSV_MINIMUM_ROW_LENGTH:
            raise forms.ValidationError('Invalid CSV header')

        return self.cleaned_data
