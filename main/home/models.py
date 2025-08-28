from django.db import models
from django.utils.translation import gettext as _
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

    def short_description(self):
        """Return a short text suitable for meta/footers based on about_us."""
        try:
            if self.about_us:
                text = str(self.about_us)
                return text[:160]
        except Exception:
            pass
        return ""

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




class MainSlider(models.Model):
    title = models.CharField(_("عنوان"), max_length=100)
    subtitle = models.CharField(_("زیرعنوان"), max_length=200, blank=True)
    image = models.ImageField(_("تصویر"), upload_to='home/slider/')
    button_text = models.CharField(_("متن دکمه"), max_length=50, default="اکنون خرید کنید")
    button_url = models.CharField(_("لینک دکمه"), max_length=200, default="/")
    is_active = models.BooleanField(_("فعال"), default=True)
    order = models.PositiveIntegerField(_("ترتیب"), default=0)

    class Meta:
        verbose_name = _("اسلایدر اصلی")
        verbose_name_plural = _("اسلایدرهای اصلی")
        ordering = ['order']

    def __str__(self):
        return self.title


class PromoCard(models.Model):
    CARD_TYPES = (
        ('large', 'کارت بزرگ'),
        ('medium', 'کارت متوسط'),
        ('small', 'کارت کوچک'),
    )

    card_type = models.CharField(_("نوع کارت"), max_length=10, choices=CARD_TYPES)
    title = models.CharField(_("عنوان"), max_length=100)
    subtitle = models.CharField(_("زیرعنوان"), max_length=200, blank=True)
    price_text = models.CharField(_("متن قیمت"), max_length=50, blank=True)
    image = models.ImageField(_("تصویر"), upload_to='home/promo/')
    button_text = models.CharField(_("متن دکمه"), max_length=50, blank=True)
    button_url = models.CharField(_("لینک دکمه"), max_length=200, blank=True)
    is_active = models.BooleanField(_("فعال"), default=True)
    order = models.PositiveIntegerField(_("ترتیب"), default=0)

    class Meta:
        verbose_name = _("کارت تبلیغاتی")
        verbose_name_plural = _("کارت‌های تبلیغاتی")
        ordering = ['order']

    def __str__(self):
        return f"{self.get_card_type_display()} - {self.title}"

class ExtraPhone(models.Model):
    phone_number = models.CharField(max_length=20, verbose_name="شماره تلفن اضافی")
    description = models.CharField(max_length=100, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "شماره تلفن اضافی"
        verbose_name_plural = "شماره‌های تلفن اضافی"

    def __str__(self):
        return self.phone_number
    

class Partner(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام شرکت/برند")
    logo = models.ImageField(upload_to='partners/logos/', verbose_name="لوگو")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    website_url = models.URLField(verbose_name="آدرس وبسایت", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "همکار"
        verbose_name_plural = "همکاران"

    def __str__(self):
        return self.name