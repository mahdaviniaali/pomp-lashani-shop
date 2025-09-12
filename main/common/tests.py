from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
import os

from carts.models import Cart, CartItem
from products.models import Product, ProductVariant
from categories.models import Category, Brand

User = get_user_model()


class CartModelTest(TestCase):
    """تست‌های مربوط به مدل Cart"""
    
    def setUp(self):
        # ایجاد کاربر تست
        self.user = User.objects.create_user(
            username="testuser",
            phone_number="09123456789",
            email="test@example.com"
        )
        
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
    
    def test_cart_creation(self):
        """تست ایجاد سبد خرید"""
        cart = Cart.objects.create(user=self.user)
        
        self.assertEqual(cart.user, self.user)
        self.assertIsNotNone(cart.created_at)
        self.assertIsNotNone(cart.update_at)
    
    def test_cart_str(self):
        """تست متد __str__ مدل Cart"""
        cart = Cart.objects.create(user=self.user)
        expected_str = f"Cart {cart.id} - {self.user.username}"
        self.assertEqual(str(cart), expected_str)
    
    def test_cart_total_items(self):
        """تست محاسبه تعداد کل آیتم‌ها در سبد خرید"""
        cart = Cart.objects.create(user=self.user)
        
        # ایجاد آیتم‌های سبد خرید
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            productvariant=self.variant,
            quantity=2,
            price=self.variant.price
        )
        
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            productvariant=self.variant,
            quantity=3,
            price=self.variant.price
        )
        
        # محاسبه تعداد کل آیتم‌ها
        total_items = sum(item.quantity for item in cart.items.all())
        self.assertEqual(total_items, 5)
    
    def test_cart_total_price(self):
        """تست محاسبه قیمت کل سبد خرید"""
        cart = Cart.objects.create(user=self.user)
        
        # ایجاد آیتم سبد خرید
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            productvariant=self.variant,
            quantity=2,
            price=self.variant.price
        )
        
        expected_total = 2 * self.variant.price  # 2 * 200000 = 400000
        self.assertEqual(cart.get_total_price(), expected_total)
    
    def test_cart_is_empty(self):
        """تست بررسی خالی بودن سبد خرید"""
        cart = Cart.objects.create(user=self.user)
        
        # سبد خرید خالی
        self.assertEqual(cart.items.count(), 0)
        
        # اضافه کردن آیتم
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            productvariant=self.variant,
            quantity=1,
            price=self.variant.price
        )
        
        self.assertEqual(cart.items.count(), 1)
    
    def test_cart_clear(self):
        """تست پاک کردن سبد خرید"""
        cart = Cart.objects.create(user=self.user)
        
        # اضافه کردن آیتم‌ها
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            productvariant=self.variant,
            quantity=2,
            price=self.variant.price
        )
        
        self.assertEqual(cart.items.count(), 1)
        
        # پاک کردن سبد خرید
        cart.items.all().delete()
        
        self.assertEqual(cart.items.count(), 0)


class CartItemModelTest(TestCase):
    """تست‌های مربوط به مدل CartItem"""
    
    def setUp(self):
        # ایجاد کاربر تست
        self.user = User.objects.create_user(
            username="testuser",
            phone_number="09123456789",
            email="test@example.com"
        )
        
        # ایجاد سبد خرید
        self.cart = Cart.objects.create(user=self.user)
        
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
    
    def test_cart_item_creation(self):
        """تست ایجاد آیتم سبد خرید"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            productvariant=self.variant,
            quantity=2,
            price=self.variant.price
        )
        
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.productvariant, self.variant)
        self.assertEqual(cart_item.quantity, 2)
    
    def test_cart_item_str(self):
        """تست متد __str__ مدل CartItem"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            productvariant=self.variant,
            quantity=2,
            price=self.variant.price
        )
        
        expected_str = f"2x {self.product.title} and variant {self.variant.id} in Cart {self.cart.id}"
        self.assertEqual(str(cart_item), expected_str)
    
    def test_cart_item_total_price(self):
        """تست محاسبه قیمت کل آیتم سبد خرید"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            productvariant=self.variant,
            quantity=3,
            price=self.variant.price
        )
        
        expected_total = 3 * self.variant.price  # 3 * 200000 = 600000
        self.assertEqual(cart_item.get_const, expected_total)
    
    def test_cart_item_properties(self):
        """تست properties مدل CartItem"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            productvariant=self.variant,
            quantity=2,
            price=self.variant.price
        )
        
        # تست property های مختلف
        self.assertTrue(cart_item.is_available)
        self.assertEqual(cart_item.remaining_stock, self.variant.stock)
        self.assertIn(self.product.title, cart_item.product_name)
        self.assertIn(self.variant.name, cart_item.product_name)
    
    def test_cart_item_methods(self):
        """تست متدهای مدل CartItem"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            productvariant=self.variant,
            quantity=2,
            price=self.variant.price
        )
        
        # تست متدهای مختلف
        self.assertTrue(cart_item.check_stock())
        self.assertEqual(cart_item.update_price(), self.variant.price)
        
        # تست set_quantity
        cart_item.set_quantity(5)
        self.assertEqual(cart_item.quantity, 5)
