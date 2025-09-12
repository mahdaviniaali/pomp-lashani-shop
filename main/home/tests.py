from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
import os

from .models import MainSlider, PromoCard, Partner, ExtraPhone, CompanyInfo, GlobalSettings
from products.models import Product
from categories.models import Category, Brand
from users.models import Address

User = get_user_model()


class HomeViewTest(TestCase):
    """تست‌های مربوط به ویو صفحه اصلی"""
    
    def setUp(self):
        """تنظیمات اولیه برای تست‌ها"""
        self.client = Client()
        cache.clear()  # پاک کردن کش قبل از هر تست
        
        # ایجاد دسته‌بندی تست
        self.category = Category.objects.create(
            title="دسته‌بندی تست",
            slug="test-category"
        )
        
        # ایجاد برند تست
        self.brand = Brand.objects.create(
            name="برند تست",
            available=True
        )
        
        # ایجاد محصول تست
        self.product = Product.objects.create(
            title="محصول تست",
            slug="test-product",
            category=self.category,
            brand=self.brand,
            available=True,
            sold_count=10,
            image=SimpleUploadedFile("product.jpg", b"file_content", content_type="image/jpeg")
        )
        
        # ایجاد اسلایدر تست
        self.slider = MainSlider.objects.create(
            title="اسلایدر تست",
            subtitle="زیرعنوان تست",
            image=SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg"),
            button_text="دکمه تست",
            button_url="/test/",
            is_active=True,
            order=1
        )
        
        # ایجاد اطلاعات شرکت برای context processor
        self.company_info = CompanyInfo.objects.create(
            name="شرکت تست",
            logo=SimpleUploadedFile("logo.jpg", b"file_content", content_type="image/jpeg"),
            about_us="درباره شرکت تست",
            contact_email="test@example.com",
            contact_phone="09123456789",
            address="آدرس شرکت تست"
        )
        
        # ایجاد تنظیمات کلی برای context processor
        self.global_settings = GlobalSettings.objects.create(
            site_title="سایت تست",
            meta_description="توضیحات متا تست",
            favicon=SimpleUploadedFile("favicon.ico", b"file_content", content_type="image/x-icon"),
            footer_text="متن فوتر تست"
        )
    
    def tearDown(self):
        """پاک کردن فایل‌های تست بعد از هر تست"""
        cache.clear()
        # پاک کردن فایل‌های آپلود شده
        for obj in [self.slider, self.company_info, self.global_settings, self.product]:
            if hasattr(obj, 'image') and obj.image and os.path.exists(obj.image.path):
                os.remove(obj.image.path)
            if hasattr(obj, 'logo') and obj.logo and os.path.exists(obj.logo.path):
                os.remove(obj.logo.path)
            if hasattr(obj, 'favicon') and obj.favicon and os.path.exists(obj.favicon.path):
                os.remove(obj.favicon.path)
    
    def test_home_view_get(self):
        """تست نمایش صفحه اصلی"""
        response = self.client.get(reverse('home:home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'اسلایدر تست')
    
    def test_home_view_caching(self):
        """تست عملکرد کش در صفحه اصلی"""
        # اولین درخواست
        response1 = self.client.get(reverse('home:home'))
        self.assertEqual(response1.status_code, 200)
        
        # حذف اسلایدر از دیتابیس
        self.slider.delete()
        
        # درخواست دوم - باید از کش استفاده کند
        response2 = self.client.get(reverse('home:home'))
        self.assertEqual(response2.status_code, 200)
        # هنوز باید اسلایدر را نشان دهد چون از کش می‌آید
        self.assertContains(response2, 'اسلایدر تست')


class AboutUsViewTest(TestCase):
    """تست‌های مربوط به ویو درباره ما"""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
        
        # ایجاد همکار تست
        self.partner = Partner.objects.create(
            name="همکار تست",
            logo=SimpleUploadedFile("partner.jpg", b"file_content", content_type="image/jpeg"),
            description="توضیحات همکار",
            website_url="https://example.com",
            is_active=True
        )
    
    def tearDown(self):
        cache.clear()
        if self.partner.logo and os.path.exists(self.partner.logo.path):
            os.remove(self.partner.logo.path)
    
    def test_about_us_view_get(self):
        """تست نمایش صفحه درباره ما"""
        response = self.client.get(reverse('home:about_us'))
        
        self.assertEqual(response.status_code, 200)
        # بررسی وجود partners در context
        self.assertIn('partners', response.context)
        # بررسی اینکه partners شامل همکار تست است
        partners = response.context['partners']
        self.assertIn(self.partner, partners)


class ConectUsViewTest(TestCase):
    """تست‌های مربوط به ویو تماس با ما"""
    
    def setUp(self):
        self.client = Client()
        
        # ایجاد شماره تلفن اضافی تست
        self.extra_phone = ExtraPhone.objects.create(
            phone_number="09123456789",
            description="شماره تست",
            is_active=True
        )
    
    def test_conect_us_view_get(self):
        """تست نمایش صفحه تماس با ما"""
        response = self.client.get(reverse('home:conect_us'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '09123456789')
        self.assertContains(response, 'شماره تست')


class UserAddressListViewTest(TestCase):
    """تست‌های مربوط به ویو لیست آدرس کاربر"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            phone_number="09123456789",
            email="test@example.com"
        )
        
        # ایجاد آدرس تست
        self.address = Address.objects.create(
            user=self.user,
            title="آدرس خانه",
            province="تهران",
            city="تهران",
            postal_code="1234567890",
            address="آدرس کامل تست",
            is_default=True
        )
    
    def test_user_address_list_view_requires_login(self):
        """تست نیاز به لاگین برای نمایش آدرس‌ها"""
        response = self.client.get(reverse('home:address'))
        
        # باید به صفحه لاگین هدایت شود
        self.assertEqual(response.status_code, 302)
    
    def test_user_address_list_view_with_login(self):
        """تست نمایش آدرس‌ها با لاگین"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('home:address'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'آدرس خانه')
