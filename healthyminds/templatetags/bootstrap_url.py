from django import template

register = template.Library()

@register.simple_tag
def sub_active_url(request, url, output=u'active'):
    # Tag that outputs text if the given url is active for the request
    if request.path.startswith(url):
        return output
    return ''
