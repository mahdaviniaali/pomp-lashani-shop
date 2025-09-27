from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateRangeFilter
from import_export.admin import ImportExportModelAdmin
from .models import Product, ProductImage, ProductAttributeValue, ProductVariant
from .widgets import CropImageWidget

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'image_preview', 'alt_text')
    readonly_fields = ('image_preview',)
    verbose_name = _("تصویر محصول")
    verbose_name_plural = _("تصاویر محصول")
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['image'].widget = CropImageWidget(target_size={'width': 800, 'height': 600})
        return formset
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "-"
    image_preview.short_description = _("پیش‌نمایش")

class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    fields = ('attribute', 'value')
    verbose_name = _("ویژگی محصول")
    verbose_name_plural = _("ویژگی‌های محصول")

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('name', 'value', 'price', 'stock', 'available', 'stock_status')
    readonly_fields = ('stock_status',)
    verbose_name = _("تنوع محصول")
    verbose_name_plural = _("تنوع محصولات")
    
    def stock_status(self, obj):
        if obj.stock > 10:
            color = 'green'
            status = _("موجود")
        elif obj.stock > 0:
            color = 'orange'
            status = _("کم موجود")
        else:
            color = 'red'
            status = _("ناموجود")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({})</span>',
            color,
            obj.stock,
            status
        )
    stock_status.short_description = _("وضعیت موجودی")

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = (
        'image_thumbnail',
        'title',
        'category_brand',
        'stock_summary',
        'available_status',
        'need_to_call_display',
    )
    
    list_filter = (
        'available',
        'category',
        'brand',
        'need_to_call',
        ('create_at', DateRangeFilter),
    )
    
    search_fields = (
        'title',
        'description',
        'category__title',
        'brand__name'
    )
    
    readonly_fields = (
        'slug',
        'create_at',
        'update_at',
        'image_preview',
        'catalog_link',
        'sold_count_display'
    )
    
    fieldsets = (
        (_("اطلاعات پایه"), {
            'fields': (
                'title',
                'slug',
                'category',
                'brand',
                'available',
                'need_to_call'
            )
        }),
        (_("تصاویر و قیمت"), {
            'fields': (
                'image',
                'image_preview',
                'discounted_price',
            )
        }),
        (_("محتوای محصول"), {
            'fields': (
                'description',
                'tags',
                'catalog_file',
                'catalog_link'
            ),
            'classes': ('collapse',)
        }),
        (_("آمار و تاریخچه"), {
            'fields': (
                'sold_count_display',
                'create_at',
                'update_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductAttributeValueInline, ProductVariantInline]
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['image'].widget = CropImageWidget(target_size={'width': 800, 'height': 600})
        return form
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "-"
    image_thumbnail.short_description = _("تصویر")
    
    def category_brand(self, obj):
        brand = f" | {obj.brand.name}" if obj.brand else ""
        return f"{obj.category.title}{brand}"
    category_brand.short_description = _("دسته‌بندی | برند")
    
   
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px;" />', obj.image.url)
        return "-"
    image_preview.short_description = _("پیش‌نمایش تصویر")
    
    def catalog_link(self, obj):
        if obj.catalog_file:
            return format_html('<a href="{}">{}</a>', obj.catalog_file.url, _("دانلود کاتالوگ"))
        return "-"
    catalog_link.short_description = _("کاتالوگ")
    
    def stock_summary(self, obj):
        variants = obj.variants.all()
        total_stock = sum(v.stock for v in variants)

        if total_stock > 10:
            color = 'green'
        elif total_stock > 0:
            color = 'orange'
        else:
            color = 'red'

        total_stock_str = f"{total_stock:,}"  # جداکننده هزارگان

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            total_stock_str
        )
    stock_summary.short_description = _("موجودی کل")
    
    def available_status(self, obj):
        if obj.available:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                _("فعال")
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">{}</span>',
            _("غیرفعال")
        )
    available_status.short_description = _("وضعیت")
    
    def need_to_call_display(self, obj):
        if obj.need_to_call:
            return format_html(
                '<span style="color: orange; font-weight: bold;">{}</span>',
                _("بله")
            )
        return format_html(
            '<span style="color: gray;">{}</span>',
            _("خیر")
        )
    need_to_call_display.short_description = _("نیاز به تماس")
    
    def sold_count_display(self, obj):
        return f"{obj.sold_count:,}"
    sold_count_display.short_description = _("تعداد فروخته شده")
    
    

@admin.register(ProductVariant)
class ProductVariantAdmin(ImportExportModelAdmin):
    list_display = (
        
        'product_link',
        'name',
        'value',
        'price_display',
        'stock_display',
        'available_display',
        'last_stock_change'
    )
    
    list_filter = (
        'available',
        'product__category',
    )
    
    search_fields = (
        'product__title',
        'name',
        'value'
    )
    
    readonly_fields = (
        'stock_history',
    )
    
    fieldsets = (
        (_("اطلاعات پایه"), {
            'fields': (
                'product',
                'name',
                'value',
                'price',
                'stock',
                'available'
            )
        }),
        (_("تاریخچه موجودی"), {
            'fields': ('stock_history',),
            'classes': ('collapse',)
        }),
    )
    
    def product_link(self, obj):
        link = reverse("admin:products_product_change", args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', link, obj.product.title)
    product_link.short_description = _("محصول")
    
    def price_display(self, obj):
        return f"{obj.price:,}"
    price_display.short_description = _("قیمت")
    
    def stock_display(self, obj):
        if obj.stock > 10:
            color = 'green'
            status = _("موجود")
        elif obj.stock > 0:
            color = 'orange'
            status = _("کم موجود")
        else:
            color = 'red'
            status = _("ناموجود")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({})</span>',
            color,
            obj.stock,
            status
        )
    stock_display.short_description = _("موجودی")
    
    def available_display(self, obj):
        if obj.available:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                _("فعال")
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">{}</span>',
            _("غیرفعال")
        )
    available_display.short_description = _("وضعیت")
    
    def last_stock_change(self, obj):
        if obj.history.exists():
            last_change = obj.history.first()
            # فقط روی آبجکت چک کن، نه در کوئری
            if hasattr(last_change, 'changes_dict') and 'stock' in last_change.changes_dict:
                return format_html(
                    '{} {} {} {}',
                    _("به"),
                    last_change.changes_dict['stock'][1],
                    _("توسط"),
                    f"{last_change.actor} ({last_change.timestamp.strftime('%Y-%m-%d %H:%M')})"
                )
        return "-"
    last_stock_change.short_description = _("آخرین تغییر")
    
    def stock_history(self, obj):
        if obj.history.exists():
            changes = []
            for entry in obj.history.all().order_by('-timestamp')[:5]:
                if hasattr(entry, 'changes_dict') and 'stock' in entry.changes_dict:
                    changes.append(
                        f"{entry.changes_dict['stock'][1]} {_('توسط')} {entry.actor} {_('در')} {entry.timestamp.strftime('%Y-%m-%d %H:%M')}"
                    )
            return format_html("<br>".join(changes)) if changes else _("بدون تغییرات")
        return _("بدون تاریخچه")
    stock_history.short_description = _("تاریخچه تغییرات موجودی")