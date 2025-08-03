# product manager
from django.db.models import  Min, Max,Subquery, Manager, QuerySet, Prefetch, Exists, Q, Case, When, Value, IntegerField, OuterRef
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType



class ProductQuerySet(QuerySet):
   

    def filter_by_params(self, params):
        from .models import ProductVariant

        # لیست فیلدهای مجاز برای مرتب‌سازی
        ordering_fields = {
            'price': 'min_price',
            '-price': '-min_price',
            'created_at': 'created_at',
            '-created_at': '-created_at',
            'sold_count': 'sold_count',
            '-sold_count': '-sold_count',
            'search': 'search',
        }

        # ساخت کوئری پایه
        queryset = (
            self.filter(
                variants__isnull=False, 
                variants__available=True
            )
            .annotate(
                min_price=Min('variants__price', 
                            filter=Q(variants__available=True, variants__stock__gt=0)),
                max_price=Max('variants__price', 
                            filter=Q(variants__available=True, variants__stock__gt=0)),
                has_stock=Exists(
                    ProductVariant.objects.filter(
                        product=OuterRef('pk'),
                        available=True,
                        stock__gt=0
                    )
                )
            )
            .filter(available=True, has_stock=True)
            .distinct()
        )
        #جستجو
        if search := params.get('search'):
            queryset = queryset.filter(title__icontains=search)

        # فیلتر قیمت
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        
        if min_price and min_price.isdigit():
            queryset = queryset.filter(min_price__gte=int(min_price))
        
        if max_price and max_price.isdigit():
            queryset = queryset.filter(max_price__lte=int(max_price))

        # فیلتر دسته‌بندی
        if category := params.get('category'):
            queryset = queryset.filter(category__id=category)

        # فیلتر چند برندی
        if brands := params.getlist('brand'):  # برای GET params مانند ?brand=apple&brand=samsung
            queryset = queryset.filter(brand__name__in=brands)
        elif brand := params.get('brand'):  # برای حالت تک برندی
            queryset = queryset.filter(brand__name__icontains=brand)

        # مرتب‌سازی
        if order := params.get('order'):
            if order_field := ordering_fields.get(order):
                queryset = queryset.order_by(order_field)


        


        return queryset



    def related_products(self, category):
        from products.models import ProductVariant
        return self.filter(category = category).annotate(
                min_price=Min('variants__price', 
                            filter=Q(variants__available=True, variants__stock__gt=0)),
                max_price=Max('variants__price', 
                            filter=Q(variants__available=True, variants__stock__gt=0)),
                has_stock=Exists(
                    ProductVariant.objects.filter(
                        product=OuterRef('pk'),
                        available=True,
                        stock__gt=0
                    )
                )).filter(available=True, has_stock=True).distinct()
        



    def with_related(self):
        ''' این متد برای بارگذاری داده‌های مرتبط با محصول استفاده می‌شود.
        '''
        from products.models import ProductVariant
        return (
            self.select_related('category', 'brand')
                        .prefetch_related(
                            'images',
                            'attributes',
                            Prefetch(
                                'variants',
                                queryset=ProductVariant.objects.filter(available=True),
                            )
                        )
                    )
    
    
    def with_related_for_home(self):
        """
        کوئری بهینه برای صفحه اصلی با اطلاعات:
        - min_price: کمترین قیمت بین واریانت‌ها (فقط واریانت‌های فعال و با موجودی)
        - max_price: بیشترین قیمت بین واریانت‌ها (فقط واریانت‌های فعال و با موجودی)
        - min_price_id: آیدی واریانتی که کمترین قیمت را دارد
        - max_price_id: آیدی واریانتی که بیشترین قیمت را دارد
        - min_price_stock: موجودی واریانت با کمترین قیمت
        - max_price_stock: موجودی واریانت با بیشترین قیمت
        - has_stock: آیا حداقل یک واریانت فعال با موجودی بیشتر از صفر وجود دارد یا خیر
        - last_stock_change: آخرین تغییر موجودی در واریانت‌ها توسط ادمین
        """
        from products.models import ProductVariant
        variant_content_type = ContentType.objects.get_for_model(ProductVariant)
        
        variant_ids = ProductVariant.objects.filter(product__in=self).values('id')
        
        last_stock_change = LogEntry.objects.filter(
            content_type=variant_content_type,
            object_id__in=Subquery(variant_ids),
            changes__has_key='stock',
            actor__is_staff=True
        ).order_by('-timestamp')
        
        # ساب‌کوئری برای پیدا کردن واریانتی که کمترین قیمت را دارد
        min_price_variant = ProductVariant.objects.filter(
            product=OuterRef('pk'),
            available=True,
            stock__gt=0
        ).order_by('price').values('id', 'stock', 'name')[:1]
        
        # ساب‌کوئری برای پیدا کردن واریانتی که بیشترین قیمت را دارد
        max_price_variant = ProductVariant.objects.filter(
            product=OuterRef('pk'),
            available=True,
            stock__gt=0
        ).order_by('-price').values('id', 'stock', 'name')[:1]
        
        return (
            self
            .filter(
                variants__isnull=False, 
                variants__available=True
            )
            .annotate(
                # محاسبه کمترین و بیشترین قیمت
                min_price=Min('variants__price', filter=Q(variants__available=True, variants__stock__gt=0)),
                max_price=Max('variants__price', filter=Q(variants__available=True, variants__stock__gt=0)),
                
                # اطلاعات واریانت با کمترین قیمت
                min_price_id=Subquery(min_price_variant.values('id')[:1]),
                min_price_stock=Subquery(min_price_variant.values('stock')[:1]),
                min_price_name=Subquery(min_price_variant.values('name')[:1]),
                
                # اطلاعات واریانت با بیشترین قیمت
                max_price_id=Subquery(max_price_variant.values('id')[:1]),
                max_price_stock=Subquery(max_price_variant.values('stock')[:1]),
                max_price_name=Subquery(max_price_variant.values('name')[:1]),
                
                # بررسی وجود موجودی
                has_stock=Case(
                    When(
                        Exists(
                            ProductVariant.objects.filter(
                                product=OuterRef('pk'), 
                                available=True, 
                                stock__gt=0
                            )
                        ),
                        then=Value(1)
                    ),
                    default=Value(0),
                    output_field=IntegerField()
                ),
                
                # اطلاعات آخرین تغییر موجودی
                last_stock_change_value=Subquery(
                    last_stock_change.values('changes__stock__1')[:1]
                ),
                last_stock_change_time=Subquery(
                    last_stock_change.values('timestamp')[:1]
                ),
                last_stock_change_variant=Subquery(
                    last_stock_change.values('object_repr')[:1]
                )
            )
            .distinct()
        )




class ProductManager(Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)
    def related_products(self, category):
        return self.get_queryset().related_products(category)
    def filter_and_order_by_params(self, params):
        return self.get_queryset().filter_by_params(params)
    def with_related(self):
        return self.get_queryset().with_related()
    def with_related_for_home(self):
        return self.get_queryset().with_related_for_home()

    
    
class ProductOptionQuerySet(QuerySet):
    def related_product(self, product):
        return self.filter(
            product=product,
            available=True
        ).select_related(
            'option',
            'option__option_type'
        )
    
    def with_option_details(self):
        return self.values(
            'option__name',
            'option__option_type__name',
            'option__price',
            'option__duration_days'
        )

class ProductOptionManager(Manager):
    def get_queryset(self):
        return ProductOptionQuerySet(self.model, using=self._db)
    
    def related_product(self, product):
        return self.get_queryset().related_product(product)
    
    def related_product_details(self, product):
        return self.related_product(product).with_option_details()