from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager, AdressManager, OTPManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog

class User(AbstractBaseUser, PermissionsMixin):
    # اطلاعات کاربری
    fullname = models.CharField(_("نام کامل"), max_length=50, blank=True)  # نام کامل (اختیاری)
    email = models.EmailField(_("ایمیل"), max_length=254, null=True, blank=True)  # ایمیل (برای ادمین الزامی)
    phone_number = models.CharField(_("شماره تلفن"), max_length=15, unique=True)  # شماره تلفن منحصر‌به‌فرد
    username = models.CharField(_("نام کاربری"), max_length=50, unique=True, blank=True)  # نام کاربری برای لاگین
    is_verified = models.BooleanField(_("تأیید شده"), default=False)  # وضعیت تأیید حساب
    available = models.BooleanField(_("فعال"), default=True)  # حساب فعال است یا خیر
    is_staff = models.BooleanField(_("دسترسی به پنل مدیریت"), default=False)  # دسترسی به ادمین
    is_superuser = models.BooleanField(_("مدیر کل"), default=False)  # دسترسی کامل
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)  # زمان ایجاد حساب
    updated_at = models.DateTimeField(_("آخرین به‌روزرسانی"), auto_now=True)  # زمان آخرین تغییرات
    nationalcode = models.CharField(_("کد ملی"), max_length=10, blank=True)
    
    objects = UserManager()  
    history = AuditlogHistoryField(null=True, blank=True)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone_number"]  # هنگام ساخت سوپر یوزر، ایمیل و شماره تلفن الزامی است

    def user_address(self):
        return list(self.addresses.all())

    def get_cart(self):
        return self.cart 

    def has_in_cart(self, product):
        return self.cart.items.filter(product=product).exists()

    def get_last_order(self):
        return self.orders.last()

    def create_order(self):
        return 
    
    def get_default_address(self):
        return self.addresses.first() 
    
    def add_and_edit_user_info(self, info):

        for field, value in info.items():
            setattr(self, field, value)
            
        self.save()
        
    def save(self, *args, **kwargs):
        """اگر نام کاربری خالی باشد، از شماره تلفن ساخته شود"""
        if not self.username:
            self.username = self.phone_number
        super().save(*args, **kwargs)
    

    class Meta:
        verbose_name = _("کاربر")
        verbose_name_plural = _("کاربران")
        ordering = ["-created_at"]

    


    def __str__(self):
        return self.username



class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name=_("کاربر"))
    title = models.CharField(_("عنوان"), max_length=100)
    province = models.CharField(_("استان"), max_length=100)
    city = models.CharField(_("شهر"), max_length=100)
    postal_code = models.CharField(_("کد پستی"), max_length=20)
    address = models.TextField(_("آدرس"))
    is_default = models.BooleanField(_("آدرس پیش‌فرض"), default=False)
    
    history = AuditlogHistoryField(null=True, blank=True)
    objects = AdressManager()  
    def __str__(self):
        return f"{self.title} - {self.city}"

    def update_address(self, user, **new_data):
      
        if self.user != user:
            raise PermissionError("شما اجازه ویرایش این آدرس را ندارید!")

        # به‌روزرسانی فقط فیلدهای موجود در new_data
        for field, value in new_data.items():
            setattr(self, field, value)
        self.save()
        return self


    class Meta:
        verbose_name = _("آدرس")
        verbose_name_plural = _("آدرس‌ها")
        ordering = ['-id']  


class OTP(models.Model):
    phone_number = models.CharField(_("شماره تلفن"), max_length=15, unique=True)
    code = models.CharField(_("کد"), max_length=6)
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    expires_at = models.DateTimeField(_("تاریخ انقضا"))
    objects = OTPManager()

    
    def is_valid(self):
        return timezone.now() < self.expires_at

    @staticmethod
    def is_valid_for_user(phone_number):
        return OTP.objects.filter(phone_number=phone_number, expires_at__gt=timezone.now()).exists()

    def __str__(self):
        return f"{self.phone_number} - {self.code}"

    class Meta:
        verbose_name = _("رمز یکبار مصرف")
        verbose_name_plural = _("رمزهای یکبار مصرف")
        ordering = ['-created_at']



#برای ثبت تغییرات 
auditlog.register(User)
auditlog.register(Address)


