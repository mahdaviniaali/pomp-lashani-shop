from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from .models import Category, Brand, AttributeTemplate, Attribute

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'logo_preview', 'available')
    list_display_links = ('indented_title',)
    list_editable = ('available',)
    search_fields = ('title',)
    list_filter = ('available', 'parent')
    readonly_fields = ('logo_preview', 'slug')
    mptt_level_indent = 30

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = 'پیش‌نمایش لوگو'

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'available')
    list_editable = ('available',)
    search_fields = ('name',)
    readonly_fields = ('logo_preview',)
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = 'پیش‌نمایش لوگو'

class AttributeInline(admin.TabularInline):
    model = Attribute.template.through
    extra = 1
    verbose_name = "ویژگی"
    verbose_name_plural = "ویژگی‌ها"

@admin.register(AttributeTemplate)
class AttributeTemplateAdmin(admin.ModelAdmin):
    list_display = ('category',)
    inlines = [AttributeInline]
    exclude = ('attributes',)  # این خط برای جلوگیری از نمایش دوگانه فیلدها

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_templates')
    search_fields = ('title',)
    filter_horizontal = ('template',)
    
    def get_templates(self, obj):
        return ", ".join([str(temp.category) for temp in obj.template.all()])
    get_templates.short_description = 'قالب‌های مرتبط'