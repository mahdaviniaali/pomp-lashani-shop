from django.db import models
from .manager import ProductManager, ProductOptionManager 
from taggit.managers import TaggableManager
from mptt.models import TreeForeignKey
from slugify import slugify
from django.utils.translation import gettext_lazy as _ 
from django_ckeditor_5.fields import CKEditor5Field
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from meta.models import ModelMeta
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit, Crop

from django.contrib.auth import get_user_model



class Product(ModelMeta, models.Model):
    title = models.CharField(_("عنوان محصول"), max_length=700)
    slug = models.SlugField(_("اسلاگ"), max_length=700, unique=True, blank=True)
    category = TreeForeignKey('categories.Category', on_delete=models.PROTECT, verbose_name=_("دسته‌بندی"))
    brand = models.ForeignKey('categories.Brand', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("برند"))
    image = ProcessedImageField(
        upload_to='products/',
        processors=[ResizeToFill(800, 600)],
        format='JPEG',
        options={'quality': 90},
        verbose_name=_("تصویر اصلی")
    )
    discounted_price = models.PositiveIntegerField(_("قیمت تخفیف‌خورده"), null=True, blank=True)
    available = models.BooleanField(_("موجود"), default=True)
    tags = TaggableManager(_("تگ‌ها"), blank=True)
    description = CKEditor5Field(_("توضیحات"), config_name='default')
    catalog_file = models.FileField(_("فایل کاتالوگ"), upload_to='catalogs/', blank=True, null=True)
    create_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    update_at = models.DateTimeField(_("تاریخ بروزرسانی"), auto_now=True)
    sold_count = models.PositiveIntegerField(_("تعداد فروخته شده"), default=0)
    need_to_call = models.BooleanField(_("نیاز به تماس دارد"), default=False)
    history = AuditlogHistoryField(_("تاریخچه"), null=True, blank=True)
    objects = ProductManager()




    def get_meta_content(self):
        import re
        plain = re.sub('<[^<]+?>', '', self.description)
        return plain.strip()[:160]



    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_meta_title(self):
        return f"{self.title} | فروشگاه پمپ‌شاپ"

    def get_meta_description(self):
        import re
        plain = re.sub('<[^<]+?>', '', self.description)
        return plain.strip()[:160]

    def get_meta_url(self):
        return self.get_absolute_url()

    def get_meta_image(self):
        return self.image.url if self.image else None

    


    class Meta:
        verbose_name = _("محصول")
        verbose_name_plural = _("محصولات")

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_("محصول"))
    image = ProcessedImageField(
        upload_to='products/',
        processors=[ResizeToFill(800, 600)],
        format='JPEG',
        options={'quality': 90},
        verbose_name=_("تصویر")
    )
    alt_text = models.CharField(_("متن جایگزین"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("تصویر محصول")
        verbose_name_plural = _("تصاویر محصول")

class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes', verbose_name=_("محصول"))
    attribute = models.ForeignKey('categories.Attribute', on_delete=models.CASCADE, verbose_name=_("ویژگی"))
    value = models.CharField(_("مقدار"), max_length=255)

    class Meta:
        verbose_name = _("مقدار ویژگی محصول")
        verbose_name_plural = _("مقادیر ویژگی محصول")

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name=_("محصول"))
    name = models.CharField(_("نام"), max_length=100)
    value = models.CharField(_("مقدار"), max_length=100)
    price = models.IntegerField(_("قیمت"))
    stock = models.IntegerField(_("موجودی"), default=0)
    available = models.BooleanField(_("فعال"), default=True)
    history = AuditlogHistoryField(_("تاریخچه"), null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("تنوع محصول")
        verbose_name_plural = _("تنوع محصولات")




###################
#-----------آپشن های محصولات-----------#
###################
class OptionType(models.Model):
    name = models.CharField(_("نام نوع آپشن"), max_length=100)
    description = models.TextField(_("توضیحات"), blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("نوع آپشن")
        verbose_name_plural = _("انواع آپشن")

class Option(models.Model):
    name = models.CharField(_("نام آپشن"), max_length=100)
    option_type = models.ForeignKey(OptionType, on_delete=models.CASCADE, related_name='options', verbose_name=_("نوع آپشن"))
    price = models.PositiveIntegerField(_("قیمت"), default=0)
    duration_days = models.IntegerField(_("مدت زمان (روز)"), null=True, blank=True)
    available = models.BooleanField(_("موجود"), default=True)
    
    def __str__(self):
        return f"{self.name} ({self.price} تومان)"
    
    class Meta:
        verbose_name = _("آپشن")
        verbose_name_plural = _("آپشن‌ها")

class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options', verbose_name=_("محصول"))
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='productoption', verbose_name=_("آپشن"))
    available = models.BooleanField(_("موجود"), default=True)
    history = AuditlogHistoryField(_("تاریخچه"), null=True, blank=True)
    objects = ProductOptionManager ()
    
    def __str__(self):
        return f"{self.product.title} - {self.option.name}"
    
    class Meta:
        verbose_name = _("آپشن محصول")
        verbose_name_plural = _("آپشن‌های محصول")
        unique_together = ('product', 'option')

auditlog.register(Product)
auditlog.register(ProductOption)
auditlog.register(ProductVariant)