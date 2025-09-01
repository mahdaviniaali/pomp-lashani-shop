from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def clean_query(context, **kwargs):
    """
    فقط پارامترهای غیرخالی و غیرتکراری را به صورت query string برمی‌گرداند.
    پارامترهای جدید (مثلاً page) را هم می‌توان override کرد.
    """
    request = context['request']
    query = request.GET.copy()
    # پارامترهای جدید را override کن
    for k, v in kwargs.items():
        if v is not None:
            query[k] = v
    # فقط پارامترهای غیرخالی را نگه دار
    clean = {k: v for k, v in query.items() if v not in [None, '', 'None'] and k != 'page'}
    return urlencode(clean)
