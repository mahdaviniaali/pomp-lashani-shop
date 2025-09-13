from django.contrib import admin
from django.utils.html import format_html
from .models import CompanyInfo, GlobalSettings, MainSlider, PromoCard, ExtraPhone, Partner

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'contact_phone', 'contact_email')
    readonly_fields = ('logo_preview', 'whatsapp_link_preview', 'social_links_preview')
    
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('name', 'logo', 'logo_preview', 'about_us')
        }),
        ('اطلاعات تماس', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('نقشه و موقعیت', {
            'fields': ('map_embed_code', 'latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('شبکه‌های اجتماعی', {
            'fields': (
                'instagram', 
                'telegram', 
                'twitter', 
                'whatsapp', 
                'whatsapp_link_preview',
                'social_links_preview'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.logo.url)
        return "لوگو آپلود نشده است"
    logo_preview.short_description = 'پیش‌نمایش لوگو'

    def whatsapp_link_preview(self, obj):
        if obj.whatsapp:
            return format_html('<a href="{}" target="_blank">لینک واتساپ</a>', obj.whatsapp_link())
        return "شماره واتساپ تنظیم نشده است"
    whatsapp_link_preview.short_description = 'واتساپ'

    def social_links_preview(self, obj):
        links = []
        if obj.instagram:
            links.append(f'<a href="{obj.instagram}" target="_blank">اینستاگرام</a>')
        if obj.telegram:
            links.append(f'<a href="{obj.telegram}" target="_blank">تلگرام</a>')
        if obj.twitter:
            links.append(f'<a href="{obj.twitter}" target="_blank">توییتر</a>')
        return format_html(' | '.join(links)) if links else "لینکی تنظیم نشده است"
    social_links_preview.short_description = 'پیش‌نمایش لینک‌ها'

    def has_add_permission(self, request):
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
        return not GlobalSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(MainSlider)
class MainSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'image_preview', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active',)
    readonly_fields = ('image_preview',)
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'subtitle', 'image', 'image_preview', 'button_text', 'button_url')
        }),
        ('تنظیمات نمایش', {
            'fields': ('is_active', 'order')
        }),
        ('رنگ‌بندی متن', {
            'fields': ('title_color', 'subtitle_color', 'button_text_color'),
            'classes': ('collapse',)
        }),
        ('اندازه فونت', {
            'fields': ('title_font_size', 'subtitle_font_size'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "تصویر آپلود نشده است"
    image_preview.short_description = 'پیش‌نمایش تصویر'

@admin.register(PromoCard)
class PromoCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'card_type', 'image_preview', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'card_type')
    readonly_fields = ('image_preview',)
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('card_type', 'title', 'subtitle', 'price_text', 'image', 'image_preview', 'button_text', 'button_url')
        }),
        ('تنظیمات نمایش', {
            'fields': ('is_active', 'order')
        }),
        ('رنگ‌بندی متن', {
            'fields': ('title_color', 'subtitle_color', 'price_text_color', 'button_text_color'),
            'classes': ('collapse',)
        }),
        ('اندازه فونت', {
            'fields': ('title_font_size', 'subtitle_font_size', 'price_font_size'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "تصویر آپلود نشده است"
    image_preview.short_description = 'پیش‌نمایش تصویر'

@admin.register(ExtraPhone)
class ExtraPhoneAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active',)

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'website_url', 'is_active')
    list_editable = ('is_active',)
    readonly_fields = ('logo_preview',)
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.logo.url)
        return "لوگو آپلود نشده است"
    logo_preview.short_description = 'پیش‌نمایش لوگو'