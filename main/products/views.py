from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator
from categories.models import Category, Brand
from .models import Product
from django.shortcuts import get_object_or_404
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


class ProductPartials(ProductBaseView):
    
    def get (self, request):
        # این متد برای نمایش لیست محصولات استفاده می‌شود.
        products = self.get_filtered_products(request)
        page_obj = self.paginate_products(request, products)
        
        # محاسبه محدوده قیمت برای محصولات فیلتر شده
        from django.db.models import Min, Max
        price_range = products.aggregate(
            min_price=Min('variants__price', filter=Q(variants__available=True, variants__stock__gt=0)),
            max_price=Max('variants__price', filter=Q(variants__available=True, variants__stock__gt=0))
        )
        
        # مقادیر پیش‌فرض اگر محصولی وجود نداره
        min_price = price_range.get('min_price', 0) or 0
        max_price = price_range.get('max_price', 1000000) or 1000000
        
        # گرد کردن به نزدیکترین 1000
        min_price = (min_price // 1000) * 1000
        max_price = ((max_price // 1000) + 1) * 1000
        
        context = {
            'page_obj': page_obj,
            'price_range': {
                'min': min_price,
                'max': max_price,
            }
        }
        return render(request, "product_cards.html", context)



class ProductListView(ProductBaseView):
    """ویو اصلی برای نمایش لیست محصولات"""
    
    def get(self, request, pk=None, slug=None):
        products = self.get_filtered_products(request)
        parent_category = None
        # فیلتر بر اساس دسته‌بندی اگر اسلاگ وجود دارد
        if pk:
            parent_category = Category.objects.get(id=pk)
            categories = parent_category.get_descendants()
            products = products.filter(category__id=pk)
        else:
            categories = Category.objects.all()
        
        brands = Brand.objects.filter(product__in=products).distinct()
        page_obj = self.paginate_products(request, products)
        
        # محاسبه محدوده قیمت واقعی محصولات
        from django.db.models import Min, Max
        price_range = Product.objects.filter(
            variants__isnull=False, 
            variants__available=True,
            variants__stock__gt=0,
            available=True
        ).aggregate(
            min_price=Min('variants__price'),
            max_price=Max('variants__price')
        )
        
        # اگر فیلتر دسته‌بندی اعمال شده، محدوده قیمت رو برای اون دسته محاسبه کن
        if pk:
            category_price_range = Product.objects.filter(
                category__id=pk,
                variants__isnull=False, 
                variants__available=True,
                variants__stock__gt=0,
                available=True
            ).aggregate(
                min_price=Min('variants__price'),
                max_price=Max('variants__price')
            )
            # اگر محصولی در این دسته وجود داره، از محدوده دسته استفاده کن
            if category_price_range['min_price'] is not None:
                price_range = category_price_range
        
        # مقادیر پیش‌فرض اگر محصولی وجود نداره
        min_price = price_range.get('min_price', 0) or 0
        max_price = price_range.get('max_price', 1000000) or 1000000
        
        # گرد کردن به نزدیکترین 1000
        min_price = (min_price // 1000) * 1000
        max_price = ((max_price // 1000) + 1) * 1000
        
        context={
            'page_obj': page_obj,
            'categories': categories,
            'brands': brands,
            'get_params': request.GET,
            'price_range': {
                'min': min_price,
                'max': max_price,
            }
        }
        if parent_category is not None:
            context['catname']=parent_category
        return render(request, 'products.html',context)



# views.py
class ProductDetailView(View):
    def get(self, request, pk, slug):
        product = get_object_or_404(Product.objects.with_related(), pk=pk)

        related_products = Product.objects.related_products(product.category).exclude(pk=product.pk)[:10]

        #بعدا اگه خواستی بزن اپشن هارم اضاف کن
        #product_option = ProductOption.objects.related_product_details(product)
        #'product_option':product_option,

        tags = product.tags.all()[:3]
        context = {
            'product': product,
            'related_products': related_products,
            'tags': tags,
            
        }
        return render(request, 'product_detail.html', context)


class PriceRangeView(View):
    """ویو برای گرفتن محدوده قیمت محصولات"""
    
    def get(self, request):
        from django.db.models import Min, Max
        from django.http import JsonResponse
        
        # فیلتر بر اساس دسته‌بندی اگر وجود دارد
        category_id = request.GET.get('category')
        products = Product.objects.filter(
            variants__isnull=False, 
            variants__available=True,
            variants__stock__gt=0,
            available=True
        )
        
        if category_id:
            products = products.filter(category__id=category_id)
        
        price_range = products.aggregate(
            min_price=Min('variants__price'),
            max_price=Max('variants__price')
        )
        
        # مقادیر پیش‌فرض اگر محصولی وجود نداره
        min_price = price_range.get('min_price', 0) or 0
        max_price = price_range.get('max_price', 1000000) or 1000000
        
        # گرد کردن به نزدیکترین 1000
        min_price = (min_price // 1000) * 1000
        max_price = ((max_price // 1000) + 1) * 1000
        
        return JsonResponse({
            'min_price': min_price,
            'max_price': max_price,
        })