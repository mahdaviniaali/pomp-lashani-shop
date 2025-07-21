from django.db import models

class CompanyInfo(models.Model):
    """
    اطلاعات کلی شرکت که در تمام صفحات سایت نمایش داده می‌شود.
    """
    name = models.CharField(max_length=255, verbose_name="نام شرکت")
    logo = models.ImageField(upload_to='logos/', verbose_name="لوگو")
    about_us = models.TextField(verbose_name="درباره ما")
    contact_email = models.EmailField(verbose_name="ایمیل تماس")
    contact_phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    address = models.TextField(verbose_name="آدرس دفتر")
    social_links = models.JSONField(verbose_name="لینک شبکه‌های اجتماعی", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "اطلاعات شرکت"
        verbose_name_plural = "اطلاعات شرکت"

class GlobalSettings(models.Model):
    """
    تنظیمات کلی سایت که در تمام صفحات اعمال می‌شود.
    """
    site_title = models.CharField(max_length=255, verbose_name="عنوان سایت")
    meta_description = models.TextField(verbose_name="توضیحات متا")
    favicon = models.ImageField(upload_to='favicons/', verbose_name="فاوآیکون")
    footer_text = models.TextField(verbose_name="متن فوتر")

    def __str__(self):
        return self.site_title

    class Meta:
        verbose_name = "تنظیمات کلی سایت"
        verbose_name_plural = "تنظیمات کلی سایت"
