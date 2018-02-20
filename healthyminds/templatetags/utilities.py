from django import template
from django.core.urlresolvers import reverse
from django.conf import settings


register = template.Library()

@register.assignment_tag
def settings_value(name):
    return getattr(settings, name, "")

@register.filter
def divide(numerator, denominator):
    return float(numerator)/float(denominator)

@register.filter
def char_length(charstring):
    return len("%s" % charstring)

@register.filter
def multiply(num1, num2):
    return float(num1)*float(num2)

@register.filter
def subtract(one, two):
    return int(one)-int(two)

@register.filter
def lookup(dict, key):
    return dict[key]

@register.simple_tag
def lookup_default(dict, key, default=None):
    if default is not None:
        return dict.get(key,default)
    return dict[key]

@register.simple_tag(takes_context=True)
def number_list(context, max, min=1):
    max=int(max)
    context['range']=[unicode(u) for u in range(min,max)]
    return ''

@register.filter
def values_list(queryset, key):
    return queryset.values_list(key, flat=True)

@register.simple_tag(takes_context=True)
def iterate(context, reset=False):
    if reset:context['iterator']=0
    elif context.get('iterator',False):
        context['iterator']+=1
    else:context['iterator']=1
    return ''

@register.simple_tag
def sub_active_url(request, url, output=u'active'):
    # Tag that outputs text if the given url is active for the request
    if request.path.startswith(url):
        return output
    return ''

@register.filter
def remainder(numerator, denominator):
    numerator = int(numerator)
    denominator = int(denominator)
    while numerator > denominator:
        numerator -= denominator
    return numerator

@register.filter
def is_false(arg):
    return arg is False or arg is None

@register.filter
def modulus(a, b):
    return a % b

@register.filter
def as_percent(num):
    num = num*100
    return round(num)

@register.filter
def class_name(obj):
    return obj.__class__.__name__
