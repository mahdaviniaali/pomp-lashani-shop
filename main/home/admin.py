from django.contrib import admin
from django.utils.html import format_html
from .models import CompanyInfo, GlobalSettings

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'contact_phone', 'contact_email')
    readonly_fields = ('logo_preview',)
    
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('name', 'logo', 'logo_preview', 'about_us')
        }),
        ('اطلاعات تماس', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('شبکه‌های اجتماعی', {
            'fields': ('social_links',),
            'classes': ('collapse',)
        }),
    )
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.logo.url)
        return "لوگو آپلود نشده است"
    logo_preview.short_description = 'پیش‌نمایش لوگو'

    def has_add_permission(self, request):
        # فقط یک رکورد اجازه دارد وجود داشته باشد
        return not CompanyInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'favicon_preview')
    readonly_fields = ('favicon_preview',)
    
    fieldsets = (
        ('تنظیمات اصلی', {
            'fields': ('site_title', 'meta_description', 'favicon', 'favicon_preview')
        }),
        ('محتوا', {
            'fields': ('footer_text',)
        }),
    )
    
    def favicon_preview(self, obj):
        if obj.favicon:
            return format_html('<img src="{}" style="max-height: 32px;" />', obj.favicon.url)
        return "فاوآیکون آپلود نشده است"
    favicon_preview.short_description = 'پیش‌نمایش فاوآیکون'

    def has_add_permission(self, request):
        # فقط یک رکورد اجازه دارد وجود داشته باشد
        return not GlobalSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False