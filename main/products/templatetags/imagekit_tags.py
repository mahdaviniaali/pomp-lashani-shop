from django import template
from imagekit.processors import ResizeToFill, ResizeToFit, Crop

register = template.Library()

# Template tags برای استفاده آسان
@register.simple_tag
def product_thumbnail_url(image_field):
    """برای تصاویر کوچک محصولات (200x200)"""
    if image_field:
        return image_field.url
    return '/static/images/default-product.png'

@register.simple_tag
def product_card_url(image_field):
    """برای کارت‌های محصول (300x200)"""
    if image_field:
        return image_field.url
    return '/static/images/default-product.png'

@register.simple_tag
def product_detail_url(image_field):
    """برای صفحه جزئیات محصول (600x400)"""
    if image_field:
        return image_field.url
    return '/static/images/default-product.png'

@register.simple_tag
def product_large_url(image_field):
    """برای تصاویر بزرگ محصولات (800x600)"""
    if image_field:
        return image_field.url
    return '/static/images/default-product.png'

@register.simple_tag
def category_logo_url(image_field):
    """برای لوگوهای دسته‌بندی (100x100)"""
    if image_field:
        return image_field.url
    return '/static/images/default-category.png'

@register.simple_tag
def brand_logo_url(image_field):
    """برای لوگوهای برند (150x100)"""
    if image_field:
        return image_field.url
    return '/static/images/default-brand.png'
