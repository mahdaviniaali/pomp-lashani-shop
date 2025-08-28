from django.contrib import admin
from django import forms
from .models import Post, Comment
from slugify import slugify


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['slug']  # حذف فیلد اسلاگ از فرم


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    readonly_fields = ['slug', 'created_at', 'published_at', 'updated_at']
    list_display = ['title', 'slug', 'author', 'status', 'published_at', 'available']
    list_filter = ['status', 'available', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'slug']
    date_hierarchy = 'published_at'
    
    # جلوگیری از ویرایش اسلاگ حتی اگر کاربر سعی کند دستکاری کند
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:  # اگر آبجکت از قبل وجود دارد (ویرایش)
            return readonly_fields + ['slug']
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        # ایجاد اسلاگ خودکار فقط هنگام ایجاد پست جدید
        if not change:  # اگر پست جدید است
            obj.slug = slugify(obj.title, allow_unicode=True)
        
        # اطمینان از اینکه اسلاگ تکراری نباشد
        original_slug = obj.slug
        counter = 1
        while Post.objects.filter(slug=obj.slug).exclude(pk=obj.pk).exists():
            obj.slug = f"{original_slug}-{counter}"
            counter += 1
        
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at', 'available']
    list_filter = ['available', 'created_at']
    search_fields = ['user__username', 'post__title', 'content']
    readonly_fields = ['created_at', 'history']
    date_hierarchy = 'created_at'