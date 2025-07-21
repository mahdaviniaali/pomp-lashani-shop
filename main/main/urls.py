"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import register_converter


class PersianSlugConverter:
    regex = r'[-\w\u0600-\u06FF]+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value

# Register the PersianSlugConverter
register_converter(PersianSlugConverter, 'persianslug')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('', include('home.urls', namespace='home')),  # صفحه اصلی
    path('users/', include('users.urls', namespace='users')),  # مدیریت کاربران
    path('otp-auth/', include('otp_auth.urls', namespace='otp_auth')),  # ارسال و تأیید رمز یکبار مصرف
    path('products/', include('products.urls', namespace='products')),  # مدیریت محصولات
    path('carts/', include('carts.urls', namespace='carts')),  # مدیریت سفارشات
    path('payments/', include('payments.urls', namespace='payments')),  # مدیریت پرداخت‌ها
    path('blog/', include('blog.urls', namespace='blog')),  # مقالات و اخبار
    path('cms/', include('cms.urls', namespace='cms')),  # مدیریت صفحات داینامیک
    path('notifications/', include('notifications.urls', namespace='notifications')),  # ارسال پیامک و نوتیفیکیشن‌ها
    path('support/', include('support.urls', namespace='support')),  # سیستم تیکت و پشتیبانی
    path('discounts/', include('discounts.urls', namespace='discounts')),  # سیستم تخفیف و کوپن
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns