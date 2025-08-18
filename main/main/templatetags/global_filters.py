from django import template

register = template.Library()

@register.filter
def persian_intcomma(value):
    if value is None:
        return ""
    value = str(value)
    return '{:,}'.format(int(value)).replace(',', '،')


@register.simple_tag(takes_context=True)
def canonical_url(context):
    """Return absolute canonical URL without query string."""
    request = context.get('request')
    try:
        return request.build_absolute_uri(request.path)
    except Exception:
        return ""


@register.simple_tag(takes_context=True)
def absolute_url(context, relative_url):
    """Convert a relative/media URL to absolute using current request base URL."""
    if not relative_url:
        return ""
    request = context.get('request')
    try:
        return request.build_absolute_uri(relative_url)
    except Exception:
        return relative_url