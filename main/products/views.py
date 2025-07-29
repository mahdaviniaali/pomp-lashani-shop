from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator
from categories.models import Category, Brand
from .models import Product, ProductOption
from django.shortcuts import get_object_or_404



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
        
        
        context = {
            'page_obj': page_obj,
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
        
        context={
            'page_obj': page_obj,
            'categories': categories,
            'brands': brands,
            'get_params': request.GET,
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