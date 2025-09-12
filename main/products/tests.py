from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
import os

from .models import Product, ProductVariant, ProductImage, ProductAttributeValue, OptionType, Option, ProductOption
from categories.models import Category, Brand, Attribute, AttributeTemplate
from .views import ProductBaseView
from home.models import CompanyInfo, GlobalSettings

User = get_user_model()


class ProductListViewTest(TestCase):
    """تست‌های مربوط به ویو لیست محصولات"""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
        
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
        
        # ایجاد محصولات تست
        self.product1 = Product.objects.create(
            title="محصول اول",
            slug="product-1",
            category=self.category,
            brand=self.brand,
            available=True,
            sold_count=5,
            image=SimpleUploadedFile("product1.jpg", b"file_content", content_type="image/jpeg")
        )
        
        self.product2 = Product.objects.create(
            title="محصول دوم",
            slug="product-2",
            category=self.category,
            brand=self.brand,
            available=True,
            sold_count=10,
            image=SimpleUploadedFile("product2.jpg", b"file_content", content_type="image/jpeg")
        )
        
        # ایجاد اطلاعات شرکت و تنظیمات کلی برای context processor
        self.company_info = CompanyInfo.objects.create(
            name="شرکت تست",
            logo=SimpleUploadedFile("logo.jpg", b"file_content", content_type="image/jpeg"),
            about_us="درباره شرکت تست",
            contact_email="test@example.com",
            contact_phone="09123456789",
            address="آدرس شرکت تست"
        )
        
        self.global_settings = GlobalSettings.objects.create(
            site_title="سایت تست",
            meta_description="توضیحات متا تست",
            favicon=SimpleUploadedFile("favicon.ico", b"file_content", content_type="image/x-icon"),
            footer_text="متن فوتر تست"
        )
    
    def tearDown(self):
        cache.clear()
        # پاک کردن فایل‌های آپلود شده
        for obj in [self.company_info, self.global_settings, self.product1, self.product2]:
            if hasattr(obj, 'logo') and obj.logo and os.path.exists(obj.logo.path):
                os.remove(obj.logo.path)
            if hasattr(obj, 'favicon') and obj.favicon and os.path.exists(obj.favicon.path):
                os.remove(obj.favicon.path)
            if hasattr(obj, 'image') and obj.image and os.path.exists(obj.image.path):
                os.remove(obj.image.path)
    
    def test_product_list_view_get(self):
        """تست نمایش لیست محصولات"""
        response = self.client.get(reverse('products:product_list'))
        
        self.assertEqual(response.status_code, 200)
        # بررسی وجود page_obj در context
        self.assertIn('page_obj', response.context)
        # بررسی اینکه محصولات در context موجود هستند
        page_obj = response.context['page_obj']
        self.assertIn(self.product1, page_obj)
        self.assertIn(self.product2, page_obj)
    
    def test_product_list_view_with_category_filter(self):
        """تست فیلتر محصولات بر اساس دسته‌بندی"""
        response = self.client.get(
            reverse('products:product_list_by_category', 
                   args=[self.category.id, self.category.slug])
        )
        
        self.assertEqual(response.status_code, 200)
        # بررسی وجود page_obj در context
        self.assertIn('page_obj', response.context)
        # بررسی اینکه محصولات در context موجود هستند
        page_obj = response.context['page_obj']
        self.assertIn(self.product1, page_obj)
        self.assertIn(self.product2, page_obj)
        self.assertIn('catname', response.context)
        self.assertEqual(response.context['catname'], self.category)


class ProductDetailViewTest(TestCase):
    """تست‌های مربوط به ویو جزئیات محصول"""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
        
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
            description="توضیحات محصول تست",
            image=SimpleUploadedFile("product.jpg", b"file_content", content_type="image/jpeg")
        )
        
        # ایجاد اطلاعات شرکت و تنظیمات کلی برای context processor
        self.company_info = CompanyInfo.objects.create(
            name="شرکت تست",
            logo=SimpleUploadedFile("logo.jpg", b"file_content", content_type="image/jpeg"),
            about_us="درباره شرکت تست",
            contact_email="test@example.com",
            contact_phone="09123456789",
            address="آدرس شرکت تست"
        )
        
        self.global_settings = GlobalSettings.objects.create(
            site_title="سایت تست",
            meta_description="توضیحات متا تست",
            favicon=SimpleUploadedFile("favicon.ico", b"file_content", content_type="image/x-icon"),
            footer_text="متن فوتر تست"
        )
    
    def tearDown(self):
        cache.clear()
        # پاک کردن فایل‌های آپلود شده
        for obj in [self.company_info, self.global_settings, self.product]:
            if hasattr(obj, 'logo') and obj.logo and os.path.exists(obj.logo.path):
                os.remove(obj.logo.path)
            if hasattr(obj, 'favicon') and obj.favicon and os.path.exists(obj.favicon.path):
                os.remove(obj.favicon.path)
            if hasattr(obj, 'image') and obj.image and os.path.exists(obj.image.path):
                os.remove(obj.image.path)
    
    def test_product_detail_view_get(self):
        """تست نمایش جزئیات محصول"""
        response = self.client.get(
            reverse('products:product_detail', 
                   args=[self.product.id, self.product.slug])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'محصول تست')
        self.assertContains(response, 'توضیحات محصول تست')
    
    def test_product_detail_view_404(self):
        """تست نمایش 404 برای محصول ناموجود"""
        response = self.client.get(
            reverse('products:product_detail', 
                   args=[99999, 'non-existent'])
        )
        
        self.assertEqual(response.status_code, 404)


class PriceRangeViewTest(TestCase):
    """تست‌های مربوط به ویو محدوده قیمت"""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
        
        # ایجاد دسته‌بندی تست
        self.category = Category.objects.create(
            title="دسته‌بندی تست",
            slug="test-category"
        )
        
        # ایجاد محصول تست
        self.product = Product.objects.create(
            title="محصول تست",
            slug="test-product",
            category=self.category,
            available=True
        )
        
        # ایجاد تنوع محصول
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name="سایز",
            value="متوسط",
            price=200000,
            stock=10,
            available=True
        )
    
    def tearDown(self):
        cache.clear()
    
    def test_price_range_view_get(self):
        """تست دریافت محدوده قیمت"""
        response = self.client.get(reverse('products:price_range'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # بررسی محتوای JSON
        import json
        data = json.loads(response.content)
        self.assertIn('min_price', data)
        self.assertIn('max_price', data)
        self.assertLessEqual(data['min_price'], data['max_price'])
