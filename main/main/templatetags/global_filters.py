from django import template
import jdatetime
from django.utils import timezone


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
    
@register.filter
def to_jalali(value, format_type='short'):
    if not value:
        return ''
    
    try:
        # تبدیل مستقیم به تاریخ شمسی بدون درنظرگیری timezone
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        
        # فرمت‌های مختلف
        if format_type == 'month_year':
            # فقط ماه و سال: "فروردین ۱۴۰۳"
            month = jalali_date.month
            year = jalali_date.year
            
            month_names = {
                1: 'فروردین',
                2: 'اردیبهشت',
                3: 'خرداد',
                4: 'تیر',
                5: 'مرداد',
                6: 'شهریور',
                7: 'مهر',
                8: 'آبان',
                9: 'آذر',
                10: 'دی',
                11: 'بهمن',
                12: 'اسفند'
            }
            
            return f"{month_names.get(month, '')} {year}"
            
        elif format_type == 'short_month':
            # ماه کوتاه و سال دو رقمی: "فروردین ۰۳"
            month = jalali_date.month
            year_short = str(jalali_date.year)[2:]
            
            month_names = {
                1: 'فروردین',
                2: 'اردیبهشت',
                3: 'خرداد',
                4: 'تیر',
                5: 'مرداد',
                6: 'شهریور',
                7: 'مهر',
                8: 'آبان',
                9: 'آذر',
                10: 'دی',
                11: 'بهمن',
                12: 'اسفند'
            }
            
            return f"{month_names.get(month, '')} {year_short}"
        
        else:
            # فرمت پیش‌فرض
            return jalali_date.strftime('%Y/%m/%d')
            
    except Exception as e:
        # در صورت خطا، تاریخ اصلی را برگردان
        return value.strftime('%Y-%m-%d') if hasattr(value, 'strftime') else str(value)