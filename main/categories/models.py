from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from slugify import slugify
from django.utils.translation import gettext_lazy as _ 


class Category(MPTTModel):
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_list_by_category', args=[self.id, self.slug])
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True , blank=True, verbose_name="اسلاگ") 
    logo  = models.ImageField(_("logo"), upload_to="catlogos/", height_field=None, width_field=None, max_length=None, blank=True, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    available = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        return '/static/images/default-category.png' 

# مدل برند محصولات
class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام برند")
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name="لوگو")
    available = models.BooleanField(default=True)
    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'

    def __str__(self):
        return self.name


# مدل قالب ویژگی برای هر دسته‌بندی
class AttributeTemplate(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="دسته‌بندی")
    

    class Meta:
        verbose_name = 'قالب ویژگی'
        verbose_name_plural = 'قالب‌های ویژگی'

    def __str__(self):
        return f"قالب ویژگی‌های {self.category}"





# مدل ویژگی محصولات
class Attribute(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان ویژگی")
    template = models.ManyToManyField(AttributeTemplate, verbose_name="تمپلیت")


    class Meta:
        verbose_name = 'ویژگی'
        verbose_name_plural = 'ویژگی‌ها'

    def __str__(self):
        return self.title

