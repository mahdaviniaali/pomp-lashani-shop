from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Cart, CartItem

class ReadOnlyCartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    max_num = 0
    can_delete = False
    
    fields = (
        'product', 
        'productvariant', 
        'quantity', 
        'price',
        'total_price',
        'stock_status',
        'Options'
    )
    
    readonly_fields = fields
    
    def total_price(self, obj):
        return f"{obj.get_const:,} تومان"
    total_price.short_description = 'قیمت کل'
    
    def stock_status(self, obj):
        if obj.is_available:
            return format_html('<span style="color: green;">✓ موجود</span>')
        return format_html('<span style="color: red;">× ناموجود</span>')
    stock_status.short_description = 'وضعیت'
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [ReadOnlyCartItemInline]
    list_display = (
        'id',
        'user',
        'total_price_display',
        'discount_price_display',
        'item_count',
        'created_at'
    )
    
    list_filter = ('user', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = (
        'user',
        'total_price',
        'discount_price',
        'created_at',
        'update_at',
        'item_count'
    )
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'total_price', 'discount_price')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'update_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"
    total_price_display.short_description = 'جمع کل'
    
    def discount_price_display(self, obj):
        return f"{obj.discount_price:,} تومان" if obj.discount_price else "-"
    discount_price_display.short_description = 'تخفیف'
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'تعداد آیتم‌ها'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

# غیرفعال کردن پنل مستقل CartItem
admin.site.unregister(CartItem) if admin.site.is_registered(CartItem) else None