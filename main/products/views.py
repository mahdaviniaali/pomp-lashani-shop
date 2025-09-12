from django.views import View
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.core.cache import cache
from categories.models import Category, Brand
from .models import Product
from django.db.models import Q



class ProductBaseView(View):
    """کلاس پایه برای عملیات مشترک محصولات"""
    paginate_by = 16  # مقدار پیش‌فرض برای صفحه‌بندی
    
    def get_filtered_products(self, request):
        """فیلتر کردن و مرتب‌سازی محصولات بر اساس پارامترهای GET"""
        return Product.objects.filter_and_order_by_params(request.GET)
    
    def paginate_products(self, request, products):
        """صفحه‌بندی محصولات"""
        paginator = Paginator(products, self.paginate_by)
        page_number = request.GET.get('page')
        return paginator.get_page(page_number)
    
    def get_price_range_cached(self, category_id=None):
        """دریافت محدوده قیمت با کش"""
        cache_key = f'price_range_{category_id or "all"}'
        price_range = cache.get(cache_key)
        
        if not price_range:
            from django.db.models import Min, Max, Q
            
            base_filter = Q(
                variants__isnull=False,
                variants__available=True,
                variants__stock__gt=0,
                available=True
            )
            
            if category_id:
                base_filter &= Q(category__id=category_id)
            
            price_range = Product.objects.filter(base_filter).aggregate(
                min_price=Min('variants__price'),
                max_price=Max('variants__price')
            )
            
            # کش برای 1 ساعت
            cache.set(cache_key, price_range, 60 * 60)
        
        return price_range
    
    def format_price_range(self, price_range):
        """فرمت کردن محدوده قیمت"""
        min_price = price_range.get('min_price', 0) or 0
        max_price = price_range.get('max_price', 1000000) or 1000000
        
        # گرد کردن به نزدیکترین 1000
        min_price = (min_price // 1000) * 1000
        max_price = ((max_price // 1000) + 1) * 1000
        
        return {'min': min_price, 'max': max_price}


class ProductPartials(ProductBaseView):
    
    def get (self, request):
        # این متد برای نمایش لیست محصولات استفاده می‌شود.
        products = self.get_filtered_products(request)
        page_obj = self.paginate_products(request, products)
        
        # محاسبه محدوده قیمت برای محصولات فیلتر شده - بهینه‌سازی شده
        price_range = self.get_price_range_cached()
        formatted_range = self.format_price_range(price_range)
        
        context = {
            'page_obj': page_obj,
            'price_range': formatted_range
        }
        return render(request, "product_cards.html", context)



class ProductListView(ProductBaseView):
    """ویو اصلی برای نمایش لیست محصولات"""
    
    def get(self, request, pk=None, slug=None):
        products = self.get_filtered_products(request)
        parent_category = None
        # فیلتر بر اساس دسته‌بندی اگر اسلاگ وجود دارد - بهینه‌سازی شده
        if pk:
            parent_category = get_object_or_404(
                Category.objects.select_related('parent'),
                id=pk
            )
            categories = parent_category.get_descendants().select_related('parent')
            products = products.filter(category__id=pk)
        else:
            categories = cache.get_or_set(
                'all_categories_optimized',
                Category.objects.filter(available=True)
                               .select_related('parent')
                               .prefetch_related('children'),
                60 * 60 * 24  # 1 روز
            )
        
        # بهینه‌سازی کوئری برندها
        brands = cache.get_or_set(
            f'brands_for_products_{pk or "all"}',
            Brand.objects.filter(
                product__in=products,
                available=True
            ).distinct().order_by('name'),
            60 * 60 * 2  # 2 ساعت
        )
        page_obj = self.paginate_products(request, products)
        
        # محاسبه محدوده قیمت واقعی محصولات - بهینه‌سازی شده
        price_range = self.get_price_range_cached(pk)
        formatted_range = self.format_price_range(price_range)
        
        context={
            'page_obj': page_obj,
            'categories': categories,
            'brands': brands,
            'get_params': request.GET,
            'price_range': formatted_range
        }
        if parent_category is not None:
            context['catname']=parent_category
        return render(request, 'products.html',context)



# views.py
class ProductDetailView(View):
    def get(self, request, pk, slug):
        product = get_object_or_404(Product.objects.with_related(), pk=pk)

        # بهینه‌سازی کوئری محصولات مرتبط
        related_products = cache.get_or_set(
            f'related_products_{product.category.id}_{product.id}',
            Product.objects.related_products(product.category)
                          .exclude(pk=product.pk)
                          .with_related_for_home()[:10],
            60 * 60 * 6  # 6 ساعت
        )

        #بعدا اگه خواستی بزن اپشن هارم اضاف کن
        #product_option = ProductOption.objects.related_product_details(product)
        #'product_option':product_option,

        # کش تگ‌ها
        tags = cache.get_or_set(
            f'product_tags_{product.id}',
            list(product.tags.all()[:3]),
            60 * 60 * 24  # 1 روز
        )
        context = {
            'product': product,
            'related_products': related_products,
            'tags': tags,
            
        }
        return render(request, 'product_detail.html', context)


class PriceRangeView(View):
    """ویو برای گرفتن محدوده قیمت محصولات - بهینه‌سازی شده"""
    
    def get(self, request):
        from django.http import JsonResponse
        
        category_id = request.GET.get('category')
        
        # استفاده از کش برای محدوده قیمت
        cache_key = f'price_range_json_{category_id or "all"}'
        price_range = cache.get(cache_key)
        
        if not price_range:
            from django.db.models import Min, Max, Q
            
            base_filter = Q(
                variants__isnull=False,
                variants__available=True,
                variants__stock__gt=0,
                available=True
            )
            
            if category_id:
                base_filter &= Q(category__id=category_id)
            
            result = Product.objects.filter(base_filter).aggregate(
                min_price=Min('variants__price'),
                max_price=Max('variants__price')
            )
            
            # فرمت کردن نتیجه
            min_price = result.get('min_price', 0) or 0
            max_price = result.get('max_price', 1000000) or 1000000
            
            min_price = (min_price // 1000) * 1000
            max_price = ((max_price // 1000) + 1) * 1000
            
            price_range = {
                'min_price': min_price,
                'max_price': max_price,
            }
            
            # کش برای 30 دقیقه
            cache.set(cache_key, price_range, 60 * 30)
        
        return JsonResponse(price_range)