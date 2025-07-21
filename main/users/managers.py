from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from random import choices
from string import digits
from django.db.models import Manager


class UserManager(BaseUserManager):
    """
    مدیریت کاربران سفارشی
    - کاربران عادی با شماره تلفن ثبت‌نام می‌کنند
    - ادمین‌ها با ایمیل و شماره تلفن ساخته می‌شوند
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        """ایجاد کاربر عادی فقط با شماره تلفن"""
        if not phone_number:
            raise ValueError(_("شماره تلفن الزامی است."))

        extra_fields.setdefault("available", True)
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, password=None, **extra_fields):
        """ایجاد ادمین با ایمیل و شماره تلفن"""
        if not email:
            raise ValueError(_("ایمیل برای ادمین الزامی است."))

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("available", True)

        user = self.create_user(phone_number, password, email=email, **extra_fields)
        return user


class OTPManager(Manager):
    '''
    منیجر برای ساختن کد 5 رقمی OTP
    '''
    def create_otp_code(self, phone_number):
        code = ''.join(choices(digits, k=5))
       
        self.update_or_create(
            phone_number=phone_number,
            defaults={"code": code, "expires_at": timezone.now() + timedelta(minutes=5)}
        )
       
        return code
    


class AdressManager(Manager):
    
    def add_address(self, user, **address_data):
       
        address = self.model(user=user)
        
        address, created = self.get_or_create(user=user, **address_data)
        
        return address.id , created
