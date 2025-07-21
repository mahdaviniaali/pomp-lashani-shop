from django.core.cache import cache
from django.http import JsonResponse
import time

class GlobalRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # تنظیمات محدودیت
        self.rate_limit = 10000  # حداکثر ۱۰۰ درخواست
        self.time_window = 60 

    def __call__(self, request):
        # ایجاد کلید منحصر به فرد برای هر کاربر/IP
        identifier = self.get_client_identifier(request)
        cache_key = f"global_rate_limit_{identifier}"
        
        # دریافت تعداد درخواست‌های فعلی
        current_requests = cache.get(cache_key, 0)
        
        if current_requests >= self.rate_limit:
            # محاسبه زمان باقیمانده تا ریست محدودیت
            reset_time = cache.ttl(cache_key)
            return JsonResponse({
                'error': 'محدودیت تعداد درخواست',
                'detail': f'شما بیش از {self.rate_limit} درخواست در {self.time_window//60} دقیقه ارسال کرده‌اید',
                'retry_after': reset_time
            }, status=429)
        
        # افزایش تعداد درخواست‌ها
        cache.set(cache_key, current_requests + 1, self.time_window)
        return self.get_response(request)

    def get_client_identifier(self, request):
        """شناسه‌ی منحصر به فرد برای هر کاربر"""
        if request.user.is_authenticated:
            return f"user_{request.user.id}"  # برای کاربران لاگین شده
        return f"ip_{request.META.get('REMOTE_ADDR')}"  # برای کاربران مهمان