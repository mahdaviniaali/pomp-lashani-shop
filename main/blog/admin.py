from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.utils.html import format_html
from .models import Post, Comment
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from import_export.admin import ImportExportModelAdmin
from import_export import resources


class PostResource(resources.ModelResource):
    class Meta:
        model = Post
        fields = ('id', 'title', 'author__username', 'status', 'published_at', 'reading_time')


class CommentResource(resources.ModelResource):
    class Meta:
        model = Comment
        fields = ('id', 'post__title', 'user__username', 'content', 'created_at', 'likes_count')


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    can_delete = True
    fields = ('user', 'content', 'created_at', 'available')
    readonly_fields = ('user', 'content', 'created_at', 'likes_count', 'available', 'parent')
    show_change_link = False  # ویرایش غیرفعال


@admin.register(Post)
class PostAdmin(ImportExportModelAdmin):
    resource_class = PostResource
    
    list_display = (
        'title', 
        'author', 
        'status', 
        'published_at', 
        'reading_time', 
        'available', 
        'image_preview',
        'created_at',
    )
    
    list_filter = (
        ('author', RelatedDropdownFilter),
        'status',
        ('published_at', DateRangeFilter),
        'available',
        ('created_at', DateTimeRangeFilter),
    )
    
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ('-published_at',)
    list_per_page = 25
    list_select_related = ('author',)
    raw_id_fields = ('author',)
    save_on_top = True
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'author', 'status', 'available')
        }),
        ('محتوای پست', {
            'fields': ('content', 'image', 'reading_time')
        }),
        ('تاریخ‌ها', {
            'fields': ('published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'پیش‌نمایش تصویر'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')
    inlines = [CommentInline]

