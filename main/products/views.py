from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator
from categories.models import Category, Brand
from .models import Product, ProductVariant
from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Subquery



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
    
    def get(self, request, slug=None):
        products = self.get_filtered_products(request)
        
        # فیلتر بر اساس دسته‌بندی اگر اسلاگ وجود دارد
        if slug:
            parent_category = Category.objects.get(slug=slug)
            categories = parent_category.get_descendants()
            products = products.filter(category__slug=slug)
        else:
            categories = Category.objects.all()
        
        brands = Brand.objects.filter(product__in=products).distinct()
        page_obj = self.paginate_products(request, products)
        
        return render(request, 'products.html', {
            'page_obj': page_obj,
            'categories': categories,
            'catname': slug,
            'brands': brands,
            'get_params': request.GET,
        })



# views.py
class ProductDetailView(View):
    def get(self, request, slug):
        product = get_object_or_404(
            Product.objects.select_related('category').with_related(),slug=slug)
        


        related_products = (
            Product.objects.filter(
                category=product.category
            )
            .exclude(id=product.id)
            .annotate(
                product_price=Subquery(
                    ProductVariant.objects.filter(
                        product=OuterRef('pk')
                    ).order_by('price')
                    .values('price')[:1]
                )
            )
            .order_by('?')[:10]
        )
        tags = product.tags.all()[:3]
        context = {
            'product': product,
            'related_products': related_products,
            'tags' : tags,
        }
        return render(request, 'product_detail.html', context)