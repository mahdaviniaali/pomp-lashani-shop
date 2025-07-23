from django.db import models

class CompanyInfo(models.Model):
    name = models.CharField(max_length=255, verbose_name="نام شرکت")
    logo = models.ImageField(upload_to='logos/', verbose_name="لوگو")
    about_us = models.TextField(verbose_name="درباره ما")
    contact_email = models.EmailField(verbose_name="ایمیل تماس")
    contact_phone = models.CharField(max_length=20, verbose_name="شماره تماس")
    address = models.TextField(verbose_name="آدرس دفتر")
    
    # فیلدهای جدید برای مپ
    map_embed_code = models.TextField(
        verbose_name=" نقشه",
        help_text="کد نقشه گوگل",
        blank=True,
        null=True
    )
    
    latitude = models.CharField(
        max_length=20,
        verbose_name="عرض جغرافیایی",
        blank=True,
        null=True
    )
    longitude = models.CharField(
        max_length=20,
        verbose_name="طول جغرافیایی",
        blank=True,
        null=True
    )
    
    # اطلاعات شبکه‌های اجتماعی به صورت فیلدهای جداگانه
    instagram = models.URLField(blank=True, null=True, verbose_name="اینستاگرام")
    telegram = models.URLField(blank=True, null=True, verbose_name="تلگرام")
    whatsapp = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="شماره واتساپ"
    )
    twitter = models.URLField(blank=True, null=True, verbose_name="توییتر")
    
    class Meta:
        verbose_name = "اطلاعات شرکت"
        verbose_name_plural = "اطلاعات شرکت"

    def __str__(self):
        return self.name

    def whatsapp_link(self):
        if self.whatsapp:
            return f"https://wa.me/{self.whatsapp}"
        return "#"

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


