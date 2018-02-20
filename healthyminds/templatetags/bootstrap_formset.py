# from django.forms.widgets import CheckboxInput, CheckboxSelectMultiple, RadioSelect
from django.template import Context
from django.template.loader import get_template
from django import template
# from django.utils.safestring import mark_safe
# from django.conf import settings

register = template.Library()

@register.filter
def as_bootstrap_formset(formset, template="bootstrap_formset/formset-form.html"):
    return get_template("bootstrap_formset/formset.html").render(
        Context({
            'formset': formset,
            'template': template
        })
    )

