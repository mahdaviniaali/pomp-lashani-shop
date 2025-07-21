# admin.py

from django.contrib import admin
from .models import Order, OrderItem, Payment, OrderShippingMethod, ShippingMethod, ShippingPrice, ShippingZone, CartNumber

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'quantity', 'price']
    can_delete = False

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ['status', 'amount', 'method', 'card_number', 'receipt_image']
    can_delete = False

class OrderShippingMethodInline(admin.StackedInline):
    model = OrderShippingMethod
    extra = 0
    readonly_fields = ['name', 'price', 'is_postpaid']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user_fullname', 'user_phone_number', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user_phone_number', 'user_email']
    readonly_fields = ['order_number', 'total_price', 'paid_price', 'created_at', 'update_at']
    inlines = [OrderItemInline, PaymentInline, OrderShippingMethodInline]

    actions = ['mark_as_paid', 'mark_as_canceled']

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(request, f"{updated} سفارش پرداختی شدند.")
    
    def mark_as_canceled(self, request, queryset):
        updated = queryset.update(status='canceled')
        self.message_user(request, f"{updated} سفارش لغو شدند.")

@admin.register(CartNumber)
class CartNumberAdmin(admin.ModelAdmin):
    list_display = ['cart_name', 'number', 'available']
    list_filter = ['available']
    search_fields = ['number']

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'active', 'is_postpaid']
    list_filter = ['active']
    search_fields = ['name']

