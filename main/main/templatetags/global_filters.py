from django import template

register = template.Library()

@register.filter
def persian_intcomma(value):
    if value is None:
        return ""
    value = str(value)
    return '{:,}'.format(int(value)).replace(',', '،')