from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import DateFieldListFilter
from rangefilter.filters import DateRangeFilter
from .models import User, Address, OTP

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('title', 'province', 'city', 'postal_code', 'address', 'is_default')
    readonly_fields = ('province', 'city', 'postal_code', 'address')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'phone_number',
        'fullname',
        'email',
        'is_active_display',
        'is_staff_display',
        'created_at_formatted'
    )
    
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_verified',
        'available',
        ('created_at', DateRangeFilter),
    )
    
    search_fields = (
        'username',
        'phone_number',
        'fullname',
        'email',
        'nationalcode'
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'last_login_display'
    )
    
    fieldsets = (
        (_("اطلاعات کاربری"), {
            'fields': (
                'username',
                'phone_number',
                'fullname',
                'email',
                'nationalcode'
            )
        }),
        (_("دسترسی‌ها"), {
            'fields': (
                'is_staff',
                'is_superuser',
                'is_verified',
                'available'
            )
        }),
        (_("تاریخ‌ها"), {
            'fields': (
                'created_at',
                'updated_at',
                'last_login_display'
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [AddressInline]
    
    def is_active_display(self, obj):
        if obj.available:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    is_active_display.short_description = _("فعال")
    
    def is_staff_display(self, obj):
        if obj.is_staff:
            return format_html('<span style="color: blue;">✓</span>')
        return format_html('<span style="color: gray;">✗</span>')
    is_staff_display.short_description = _("کارمند")
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_formatted.short_description = _("تاریخ ثبت‌نام")
    
    def last_login_display(self, obj):
        if obj.last_login:
            return obj.last_login.strftime('%Y-%m-%d %H:%M')
        return _("هرگز")
    last_login_display.short_description = _("آخرین ورود")

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = (
        'phone_number',
        'code',
        'created_at',
        'expires_at',
        'is_valid_display'
    )
    
    list_filter = (
        ('created_at', DateRangeFilter),
    )
    
    search_fields = (
        'phone_number',
        'code'
    )
    
    readonly_fields = (
        'created_at',
        'expires_at',
    )
    
    def is_valid_display(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    is_valid_display.short_description = _("معتبر")