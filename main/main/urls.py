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
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.utils.text import slugify
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product
from blog.models import Post
from categories.models import Category
from django.conf import settings
from django.conf.urls.static import static
from django.urls import register_converter
import re


class PersianSlugConverter:
    # الگوی بهبود یافته برای اسلاگ‌های فارسی/انگلیسی
    regex = r'[\w\-_[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF}]+'
    
    def to_python(self, value):
        return value
    
    def to_url(self, value):
        # اطمینان از URL-safe بودن مقدار
        return re.sub(r'[^\w\-_[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]]', '', value)

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
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),  # داشبورد مدیریت
    path('sitemap.xml', sitemap, {'sitemaps': {
        'products': type('ProductSitemap', (Sitemap,), {
            'changefreq': 'daily',
            'priority': 0.8,
            'items': staticmethod(lambda: Product.objects.filter(available=True)),
            'location': staticmethod(lambda obj: reverse('products:product_detail', args=[obj.id, obj.slug])),
            'lastmod': staticmethod(lambda obj: obj.update_at),
        })(),
        'blog': type('PostSitemap', (Sitemap,), {
            'changefreq': 'weekly',
            'priority': 0.6,
            'items': staticmethod(lambda: Post.objects.filter(available=True)),
            'location': staticmethod(lambda obj: reverse('blog:blogdetail', args=[obj.id, obj.slug])),
            'lastmod': staticmethod(lambda obj: obj.updated_at),
        })(),
        'categories': type('CategorySitemap', (Sitemap,), {
            'changefreq': 'weekly',
            'priority': 0.5,
            'items': staticmethod(lambda: Category.objects.filter(available=True)),
            'location': staticmethod(lambda obj: reverse('products:product_list_by_category', args=[obj.id, obj.slug])),
        })(),
        'static': type('StaticViewSitemap', (Sitemap,), {
            'changefreq': 'monthly',
            'priority': 0.5,
            'items': staticmethod(lambda: ['home:home', 'home:about_us', 'home:conect_us', 'products:product_list', 'blog:bloglist']),
            'location': staticmethod(lambda name: reverse(name)),
        })(),
    }}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


# Simple robots.txt
@require_GET
def robots_txt(_request):
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        'Allow: /static/',
        'Sitemap: ' + (_request.build_absolute_uri('/sitemap.xml') if _request else '/sitemap.xml')
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

urlpatterns += [
    path('robots.txt', robots_txt, name='robots_txt')
]

# Custom error handlers
handler404 = 'main.views.custom_404_view'