import logging
import json
from datetime import datetime, date, timedelta
from django.core.urlresolvers import reverse_lazy, resolve, reverse
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django import forms
from django.forms.utils import from_current_timezone, to_current_timezone
from django.forms.models import modelformset_factory
from django.views.generic import TemplateView, View

from django.http import HttpResponseForbidden

from tracking.models import Event
from tracking.utils import create_event, UserLogPageViewMixin
from tracking.views import RecordEventView

logger = logging.getLogger(__name__)

class ObjectListView(TemplateView):
    model = None
    context_name = 'object_list'
    edit_pattern = None
    create_pattern = None

    def get_context_data(self, **kwargs):
        context = super(ObjectListView, self).get_context_data(**kwargs)
        context[self.context_name] = self.get_queryset()
        context['edit_pattern'] = self.edit_pattern
        context['create_pattern'] = self.create_pattern
        return context

    def get_queryset(self):
        return self.model.objects.all()

    def get_create_url(self):
        return reverse_lazy(self.create_pattern, kwargs=self.get_create_kwargs())

    def get_create_kwargs(self):
        return {}

class RedirectMixin(object):
    redirect_pattern = None
    redirect_kwargs = None

    def get_redirect_kwargs(self):
        return self.redirect_kwargs or {}

    def get_redirect_url(self):
        return reverse_lazy(self.redirect_pattern,
            kwargs=self.get_redirect_kwargs())

    def get_success_url(self):
        return self.get_redirect_url()

    def get_cancel_url(self):
        return self.get_redirect_url()

class SingleObjectMixin(object):
    model = None
    obj = None

    def get(self, request, obj_id, *args, **kwargs):
        self.get_object(obj_id)
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_object(self, obj_id=None):
        if not self.obj and obj_id:
            self.obj = self.get_queryset().get(id=obj_id)
        return self.obj

    def get_queryset(self):
        return self.model.objects.all()

    def post(self, request, obj_id, *args, **kwargs):
        self.get_object(obj_id)
        return self.render_to_response(self.get_context_data(**kwargs))

class ModelFormsetMixin(object):
    formset = None
    formset_model = None
    formset_form = None
    formset_extra = 0
    formset_delete = True
    formset_exclude = None

    def get_formset_queryset(self):
        return self.formset_model.objects.all()

    def create_formset(self, *args, **kwargs):
        return modelformset_factory(self.formset_model, exclude=self.formset_exclude, form=self.formset_form,
                                    extra=self.formset_extra, can_delete=self.formset_delete, *args, **kwargs)

    def get_formset(self, *args, **kwargs):
        if not self.formset:
            self.formset = self.create_formset()(queryset=self.get_formset_queryset(),
                                                 form_kwargs=self.get_form_kwargs(), *args, **kwargs)
        return self.formset

    def get_form_kwargs(self):
        return {}

class FormParamMixin(object):

    def get_form_params(self):
        return {}

    def get_save_params(self):
        return {}

    def postsave_handler(self, obj):
        pass

class CreateObjectView(RedirectMixin, FormParamMixin, TemplateView):
    form = None
    context_formname = 'form'

    def get(self, request, *args, **kwargs):
        self.obj_form = self.form(**self.get_form_params())
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super(CreateObjectView, self).get_context_data(**kwargs)
        context[self.context_formname] = self.obj_form
        context['cancel_url'] = self.get_cancel_url()
        return context

    def post(self, request, *args, **kwargs):
        self.obj_form = self.form(data=request.POST, files=request.FILES, **self.get_form_params())
        if self.obj_form.is_valid():
            obj = self.obj_form.save(**self.get_save_params())
            self.postsave_handler(obj)
            return redirect(self.get_redirect_url())
        return self.render_to_response(self.get_context_data(**kwargs))

class UpdateFormsMixin(FormParamMixin, SingleObjectMixin):
    forms = {}
    form_instance = {}

    def get(self, request, obj_id, *args, **kwargs):
        self.get_object(obj_id)
        kwargs.update(self.set_forms())
        return self.render_to_response(self.get_context_data(**kwargs))

    def set_forms(self, *args):
        obj = self.get_object()
        for attr, form in self.forms.items():
            setattr(self, attr, form(instance=self.form_instance.get(attr)(obj), *args))
        return {form:getattr(self,form) for form in self.forms}

    def post(self, request, pid, *args, **kwargs):
        self.get_object(pid)
        forms = self.set_forms(request.POST, request.FILES)

        if all([form.is_valid() for form in forms.values()]):
            for form in forms.values():
                form.save()
            self.postsave_handler()
            return redirect(self.get_success_url())
        kwargs.update(forms)
        return self.render_to_response(self.get_context_data(**kwargs))

class UpdateObjectView(RedirectMixin, UpdateFormsMixin, TemplateView):
    form = None
    context_formname = 'form'

    def get(self, request, obj_id, *args, **kwargs):
        self.get_object(obj_id)
        self.obj_form = self.form(instance=self.get_object(), **self.get_form_params())
        return self.render_to_response(self.get_context_data(**kwargs))

    def set_forms(self, *args):
        self.obj_form = self.form(instance=self.get_object())

    def get_context_data(self, **kwargs):
        context = super(UpdateObjectView, self).get_context_data(**kwargs)
        context[self.context_formname] = self.obj_form
        return context

    def post(self, request, obj_id, *args, **kwargs):
        self.get_object(obj_id)
        self.obj_form = self.form(request.POST, request.FILES, instance=self.get_object(), **self.get_form_params())
        if self.obj_form.is_valid():
            obj = self.obj_form.save(**self.get_save_params())
            self.postsave_handler(obj)
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(**kwargs))

class DeleteItemMixin(object):
    delete_permission = None

    def can_delete(self):
        return (getattr(self.request.user, self.delete_permission)
                if self.delete_permission else False)

    def delete_obj(self):
        if not self.can_delete():
            return HttpResponseForbidden()
        self.obj.delete()

class UpdateOrDeleteView(DeleteItemMixin, UpdateObjectView):
    delete_permission = 'is_staff'

    def get_context_data(self, **kwargs):
        context = super(UpdateObjectView, self).get_context_data(**kwargs)
        context[self.context_formname] = self.obj_form
        context["can_delete"] = self.can_delete()
        return context

    def post(self, request, obj_id, *args, **kwargs):
        self.obj = self.get_object(obj_id)
        self.obj_form = self.form(data=request.POST, files=request.FILES,
                            instance=self.obj, **self.get_form_params())
        if 'delete' in self.request.POST:
            self.delete_obj()
            return redirect(self.get_success_url())
        if self.obj_form.is_valid():
            obj = self.obj_form.save(**self.get_save_params())
            self.postsave_handler(obj)
            return redirect(self.get_success_url())
        return self.render_to_response(self.get_context_data(**kwargs))

class ResponseTypeMixin(object):
    content_type = None

    def get_content_type(self):
        return self.content_type

class JSONResponseMixin(ResponseTypeMixin):
    content_type = "application/json"

class CSVResponseMixin(ResponseTypeMixin):
    content_type = 'text/csv'

class JSONResponseView(JSONResponseMixin, View):

    def get(self, request, *args, **kwargs):
        return self.return_json(self.assemble_json(**kwargs))

    def assemble_json(self, **kwargs):
        return kwargs

    def return_json(self, context):
        return HttpResponse(json.dumps(context), content_type=self.get_content_type())

class DataPathMixin(object):
    data_path = None

    def get_data_file(self):
        return os.path.join(settings.PROJECT_ROOT, self.data_path)

class JSONDataMixin(DataPathMixin):

    def assemble_json(self, **kwargs):
        with open(self.get_data_file()) as data_file:
            data = json.load(data_file)
        return data

class QuerysetFilter(object):
    model = None

    def __init__(self, filter=None, **kwargs):
        self.object_list = (self.qs_filter(filter, **kwargs) if filter
                            else self.get_queryset(**kwargs))

    def get_queryset(self, **kwargs):
        return self.model.objects.filter(**self.get_default_filter())

    def qs_filter(self, filter, **kwargs):
        return self.get_queryset(**kwargs)

    def get_default_filter(self):
        return {}

class ModalFormMixin(object):
    full_page_template_name = None
    submit_pattern = None

    def use_full_page_template(self):
        self.template_name = self.full_page_template_name

    def get_submit_params(self):
        return {}

    def get_submit_url(self):
        return reverse_lazy(self.submit_pattern, kwargs=self.get_submit_params())

    def is_ajax_request(self):
        return self.request.is_ajax()

class ModelFormsetMixin(object):
    formset = None
    formset_model = None
    formset_form = None
    formset_extra = 0
    formset_delete = True
    formset_validate_min = False
    formset_min_num = 0

    def get_formset_queryset(self):
        return self.formset_model.objects.all()

    def create_formset(self):
        return modelformset_factory(self.formset_model, form=self.formset_form,
                                    extra=self.formset_extra, can_delete=self.formset_delete,
                                    validate_min=self.formset_validate_min, min_num=self.formset_min_num)

    def get_formset(self, *args, **kwargs):
        if not self.formset:
            self.formset = self.create_formset()(queryset=self.get_formset_queryset(),
                                                 form_kwargs=self.get_form_kwargs(), *args, **kwargs)
        return self.formset

    def get_form_kwargs(self):
        return {}

#===============================================================================
# Form Objects
#===============================================================================

class OneOrManyModelChoiceField(forms.ModelChoiceField):

    def to_python(self, value):
        if value and not isinstance(value, list):
            value = [value]
        return super(OneOrManyModelChoiceField, self).to_python(value)

class OneOrManyChoiceField(forms.ChoiceField):

    def to_python(self, value):
        if value and not isinstance(value, list):
            value = [value]
        return super(OneOrManyModelChoiceField, self).to_python(value)

class CompletionDateField(forms.DateTimeField):

    def to_python(self,value):
        if isinstance(value,datetime.datetime):
            return value
        elif value:
            return datetime.datetime.now()
        return None

class OptionalDateTimeField(forms.SplitDateTimeField):

    def __init__(self, input_date_formats=None, input_time_formats=None, *args, **kwargs):
        errors = self.default_error_messages.copy()
        if 'error_messages' in kwargs:
            errors.update(kwargs['error_messages'])
        localize = kwargs.get('localize', False)
        fields = (
            forms.DateField(input_formats=input_date_formats,
                      error_messages={'invalid': errors['invalid_date']},
                      localize=localize),
            forms.TimeField(input_formats=input_time_formats, required=False,
                      error_messages={'invalid': errors['invalid_time']},
                      localize=localize),
        )
        super(forms.SplitDateTimeField, self).__init__(fields, *args, **kwargs)


    def compress(self, data_list):
        if data_list:
            # Raise a validation error if time or date is empty
            # (possible if SplitDateTimeField has required=False).
            if data_list[0] in self.empty_values:
                raise ValidationError(self.error_messages['invalid_date'], code='invalid_date')
            if data_list[1] in self.empty_values:
                return from_current_timezone(data_list[0])
                #raise ValidationError(self.error_messages['invalid_time'], code='invalid_time')
            result = datetime.combine(*data_list)
            return from_current_timezone(result)
        return None


class DateTimeWidget(forms.MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """
    supports_microseconds = False
    VALID_TIME_INPUT_FORMATS = [
        '%H:%M:%S',     # '14:30:59'
        '%H:%M:%S.%f',  # '14:30:59.000200'
        '%H:%M',        # '14:30'
        '%I:%M %p',     # "5:30 PM".
    ]

    def __init__(self, attrs=None, date_format=None, time_format=None, date_attrs=None, time_attrs=None):
        date_attrs.update(attrs or {})
        time_attrs.update(attrs or {})
        widgets = (forms.DateInput(attrs=date_attrs, format=date_format),
                   forms.TimeInput(attrs=time_attrs, format=time_format))
        super(DateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            value = to_current_timezone(value)
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]
