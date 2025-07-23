from django.core.cache import cache
from home.models import CompanyInfo, GlobalSettings
from categories.models import Category  # فرض میکنیم مدل Category در اپ products است
from carts.models import Cart, CartItem
import logging

CACHE_TIMEOUT = 60 * 60 * 24  # 24 ساعت
CATEGORY_CACHE_TIMEOUT = 60 * 30  # 30 دقیقه برای کش دسته‌بندی‌ها
logger = logging.getLogger(__name__)

def get_company_info():
    cache_key = 'company_info'
    data = cache.get(cache_key)
    if not data:
        data = CompanyInfo.objects.first()
        cache.set(cache_key, data, CACHE_TIMEOUT)
    return data

def get_global_settings():
    cache_key = 'global_settings'
    data = cache.get(cache_key)
    if not data:
        data = GlobalSettings.objects.first()
        cache.set(cache_key, data, CACHE_TIMEOUT)
    return data

def get_categories():
    cache_key = 'all_categories'
    data = cache.get(cache_key)
    if not data:
        # دریافت دسته‌بندی‌های اصلی و فرزندان آنها
        data = Category.objects.filter(parent__isnull=True).prefetch_related('children').all()
        cache.set(cache_key, data, CATEGORY_CACHE_TIMEOUT)
    return data

def get_global_cart(request):
    if request.user.is_authenticated:
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            return CartItem.objects.filter(cart=cart).count()
        except Exception as e:
            logger.error(f"Error in authenticated user cart: {e}")
            return 0
    elif 'cart' in request.session:
        try:
            return len(request.session['cart'].get('items', []))
        except Exception as e:
            logger.error(f"Error in session cart: {e}")
            return 0
    else:
        return 0

def global_context(request):
    context = {}
    
    try:
        # اضافه کردن company_info
        company_info = get_company_info()
        if company_info:
            context['company_info'] = company_info
            
        # اضافه کردن global_settings
        global_settings = get_global_settings()
        if global_settings:
            context['global_settings'] = global_settings
            
        # اضافه کردن دسته‌بندی‌ها
        categories = get_categories()
        context['categories'] = categories
            
        # همیشه cart_count را اضافه کنید، حتی اگر 0 باشد
        context['cart_count'] = get_global_cart(request)

    except Exception as e:
        logger.error(f"Error in global context processor: {e}")
    
    return context