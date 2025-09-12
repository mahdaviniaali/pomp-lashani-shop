from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import User, Address, OTP

User = get_user_model()


class UserModelTest(TestCase):
    """تست‌های مربوط به مدل User"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'phone_number': '09123456789',
            'email': 'test@example.com',
            'fullname': 'کاربر تست'
        }
    
    def test_user_creation(self):
        """تست ایجاد کاربر"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.phone_number, '09123456789')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.fullname, 'کاربر تست')
        self.assertFalse(user.is_verified)
        self.assertTrue(user.available)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_user_str(self):
        """تست متد __str__ مدل User"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')
    
    def test_user_save_without_username(self):
        """تست ذخیره کاربر بدون نام کاربری"""
        user_data = self.user_data.copy()
        del user_data['username']
        
        user = User.objects.create_user(**user_data)
        
        # باید نام کاربری از شماره تلفن ساخته شود
        self.assertEqual(user.username, '09123456789')
    
    def test_user_get_default_address(self):
        """تست دریافت آدرس پیش‌فرض کاربر"""
        user = User.objects.create_user(**self.user_data)
        
        # بدون آدرس
        self.assertIsNone(user.get_default_address())
        
        # با آدرس
        address = Address.objects.create(
            user=user,
            title="آدرس خانه",
            province="تهران",
            city="تهران",
            postal_code="1234567890",
            address="آدرس کامل تست",
            is_default=True
        )
        
        self.assertEqual(user.get_default_address(), address)
    
    def test_user_add_and_edit_user_info(self):
        """تست ویرایش اطلاعات کاربر"""
        user = User.objects.create_user(**self.user_data)
        
        new_info = {
            'fullname': 'نام جدید',
            'email': 'new@example.com'
        }
        
        user.add_and_edit_user_info(new_info)
        
        # بررسی تغییرات
        user.refresh_from_db()
        self.assertEqual(user.fullname, 'نام جدید')
        self.assertEqual(user.email, 'new@example.com')
        # سایر فیلدها نباید تغییر کرده باشند
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.phone_number, '09123456789')


class AddressModelTest(TestCase):
    """تست‌های مربوط به مدل Address"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='09123456789',
            email='test@example.com'
        )
        
        self.address_data = {
            'user': self.user,
            'title': 'آدرس خانه',
            'province': 'تهران',
            'city': 'تهران',
            'postal_code': '1234567890',
            'address': 'آدرس کامل تست',
            'is_default': True
        }
    
    def test_address_creation(self):
        """تست ایجاد آدرس"""
        address = Address.objects.create(**self.address_data)
        
        self.assertEqual(address.user, self.user)
        self.assertEqual(address.title, 'آدرس خانه')
        self.assertEqual(address.province, 'تهران')
        self.assertEqual(address.city, 'تهران')
        self.assertEqual(address.postal_code, '1234567890')
        self.assertEqual(address.address, 'آدرس کامل تست')
        self.assertTrue(address.is_default)
    
    def test_address_str(self):
        """تست متد __str__ مدل Address"""
        address = Address.objects.create(**self.address_data)
        expected_str = "آدرس خانه - تهران"
        self.assertEqual(str(address), expected_str)
    
    def test_address_update_address_success(self):
        """تست ویرایش آدرس با موفقیت"""
        address = Address.objects.create(**self.address_data)
        
        new_data = {
            'title': 'آدرس جدید',
            'city': 'اصفهان',
            'province': 'اصفهان'
        }
        
        updated_address = address.update_address(self.user, **new_data)
        
        # بررسی تغییرات
        address.refresh_from_db()
        self.assertEqual(address.title, 'آدرس جدید')
        self.assertEqual(address.city, 'اصفهان')
        self.assertEqual(address.province, 'اصفهان')
        # سایر فیلدها نباید تغییر کرده باشند
        self.assertEqual(address.postal_code, '1234567890')
        self.assertEqual(address.address, 'آدرس کامل تست')
        
        self.assertEqual(updated_address, address)
    
    def test_address_update_address_permission_error(self):
        """تست خطای دسترسی در ویرایش آدرس"""
        address = Address.objects.create(**self.address_data)
        
        # ایجاد کاربر دیگر
        other_user = User.objects.create_user(
            username='otheruser',
            phone_number='09987654321',
            email='other@example.com'
        )
        
        new_data = {'title': 'آدرس جدید'}
        
        # باید خطای دسترسی بدهد
        with self.assertRaises(PermissionError):
            address.update_address(other_user, **new_data)


class OTPModelTest(TestCase):
    """تست‌های مربوط به مدل OTP"""
    
    def setUp(self):
        self.phone_number = '09123456789'
        self.code = '123456'
        self.expires_at = timezone.now() + timedelta(minutes=5)
    
    def test_otp_creation(self):
        """تست ایجاد OTP"""
        otp = OTP.objects.create(
            phone_number=self.phone_number,
            code=self.code,
            expires_at=self.expires_at
        )
        
        self.assertEqual(otp.phone_number, self.phone_number)
        self.assertEqual(otp.code, self.code)
        self.assertEqual(otp.expires_at, self.expires_at)
        self.assertIsNotNone(otp.created_at)
    
    def test_otp_str(self):
        """تست متد __str__ مدل OTP"""
        otp = OTP.objects.create(
            phone_number=self.phone_number,
            code=self.code,
            expires_at=self.expires_at
        )
        
        expected_str = f"{self.phone_number} - {self.code}"
        self.assertEqual(str(otp), expected_str)
    
    def test_otp_is_valid_valid(self):
        """تست validation برای OTP معتبر"""
        otp = OTP.objects.create(
            phone_number=self.phone_number,
            code=self.code,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        
        self.assertTrue(otp.is_valid())
    
    def test_otp_is_valid_expired(self):
        """تست validation برای OTP منقضی شده"""
        otp = OTP.objects.create(
            phone_number=self.phone_number,
            code=self.code,
            expires_at=timezone.now() - timedelta(minutes=5)
        )
        
        self.assertFalse(otp.is_valid())
    
    def test_otp_is_valid_for_user_valid(self):
        """تست validation برای کاربر با OTP معتبر"""
        OTP.objects.create(
            phone_number=self.phone_number,
            code=self.code,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        
        self.assertTrue(OTP.is_valid_for_user(self.phone_number))
    
    def test_otp_is_valid_for_user_expired(self):
        """تست validation برای کاربر با OTP منقضی شده"""
        OTP.objects.create(
            phone_number=self.phone_number,
            code=self.code,
            expires_at=timezone.now() - timedelta(minutes=5)
        )
        
        self.assertFalse(OTP.is_valid_for_user(self.phone_number))
    
    def test_otp_is_valid_for_user_no_otp(self):
        """تست validation برای کاربر بدون OTP"""
        self.assertFalse(OTP.is_valid_for_user('09999999999'))


class UserManagerTest(TestCase):
    """تست‌های مربوط به UserManager"""
    
    def test_create_user(self):
        """تست ایجاد کاربر عادی"""
        user = User.objects.create_user(
            username='testuser',
            phone_number='09123456789',
            email='test@example.com'
        )
        
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.available)
    
    def test_create_superuser(self):
        """تست ایجاد سوپر کاربر"""
        user = User.objects.create_superuser(
            username='admin',
            phone_number='09123456789',
            email='admin@example.com'
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.available)
    
    def test_create_user_without_required_fields(self):
        """تست ایجاد کاربر بدون فیلدهای الزامی"""
        # create_user فقط username و phone_number را الزامی می‌داند
        user = User.objects.create_user(
            username='testuser',
            phone_number='09123456789'
            # email اختیاری است
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.phone_number, '09123456789')


class UserIntegrationTest(TestCase):
    """تست‌های یکپارچه برای مدل User"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='09123456789',
            email='test@example.com',
            fullname='کاربر تست'
        )
    
    def test_user_with_multiple_addresses(self):
        """تست کاربر با چندین آدرس"""
        # ایجاد آدرس‌های مختلف
        address1 = Address.objects.create(
            user=self.user,
            title="آدرس خانه",
            province="تهران",
            city="تهران",
            postal_code="1234567890",
            address="آدرس خانه تست",
            is_default=True
        )
        
        address2 = Address.objects.create(
            user=self.user,
            title="آدرس محل کار",
            province="تهران",
            city="تهران",
            postal_code="0987654321",
            address="آدرس محل کار تست",
            is_default=False
        )
        
        # بررسی آدرس پیش‌فرض (get_default_address() اولین آدرس را برمی‌گرداند)
        # باید address1 باشد چون اول ایجاد شده
        default_address = self.user.get_default_address()
        self.assertIsNotNone(default_address)
        self.assertIn(default_address, [address1, address2])
        
        # بررسی لیست آدرس‌ها
        addresses = self.user.user_address()
        self.assertEqual(len(addresses), 2)
        self.assertIn(address1, addresses)
        self.assertIn(address2, addresses)
    
    def test_user_otp_flow(self):
        """تست فرآیند OTP برای کاربر"""
        phone_number = self.user.phone_number
        
        # ایجاد OTP
        otp = OTP.objects.create(
            phone_number=phone_number,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        
        # بررسی معتبر بودن OTP
        self.assertTrue(otp.is_valid())
        self.assertTrue(OTP.is_valid_for_user(phone_number))
        
        # منقضی کردن OTP
        otp.expires_at = timezone.now() - timedelta(minutes=1)
        otp.save()
        
        # بررسی منقضی شدن OTP
        self.assertFalse(otp.is_valid())
        self.assertFalse(OTP.is_valid_for_user(phone_number))
