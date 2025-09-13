from django.db import models
from products.models import Product, ProductVariant
from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from .manager import CartItemManager, CartManager
from django.utils.translation import gettext_lazy as _ 
User = get_user_model()



class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    total_price = models.IntegerField(default=0)
    discount_price = models.IntegerField(null=True, blank=True, default=0)
    sheba_number = models.CharField(_("شماره شبا"), max_length=26, blank=True, null=True, help_text="شماره شبا 24 رقمی")
    created_at = models.DateTimeField(auto_now_add=True)
    update_at= models.DateTimeField(auto_now=True)
    objects = CartManager()
    def get_total_price(self):
        return self.items.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
    
    def get_final_price(self):
        """محاسبه قیمت نهایی با در نظر گرفتن هزینه ارسال"""
        total = self.get_total_price()
        # اضافه کردن هزینه ارسال به قیمت نهایی اگر پس‌کرایه نباشد
        if hasattr(self, 'shipping_method') and self.shipping_method and not self.shipping_method.is_postpaid and self.shipping_method.price:
            total += self.shipping_method.price
        return total
    
    def update_total_price(self):
        self.total_price = self.get_final_price()
        self.save()


    def final_check_price(self):
        if self.get_final_price() == self.total_price:
            return self.total_price, True
        else:
            return False

    def clean_sheba_number(self):
        """پاک کردن و فرمت کردن شماره شبا"""
        if self.sheba_number:
            # حذف فاصله و کاراکترهای اضافی
            cleaned = self.sheba_number.replace(' ', '').replace('-', '').replace('_', '')
            # تبدیل به حروف بزرگ
            return cleaned.upper()
        return None
    
    def is_valid_sheba(self):
        """اعتبارسنجی شماره شبا"""
        if not self.sheba_number:
            return False
        
        sheba = self.clean_sheba_number()
        if not sheba or len(sheba) != 24:
            return False
        
        # بررسی اینکه با IR شروع شود
        if not sheba.startswith('IR'):
            return False
        
        # بررسی اینکه بقیه کاراکترها عدد باشند
        if not sheba[2:].isdigit():
            return False
        
        return True
    
    def get_formatted_sheba(self):
        """دریافت شماره شبا با فرمت مناسب"""
        if not self.sheba_number:
            return None
        
        sheba = self.clean_sheba_number()
        if not sheba:
            return None
        
        # فرمت کردن: IR12 3456 7890 1234 5678 9012 34
        formatted = f"{sheba[:4]} {sheba[4:8]} {sheba[8:12]} {sheba[12:16]} {sheba[16:20]} {sheba[20:24]}"
        return formatted

    def __str__(self):
        return f"Cart {self.id} - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items') 
    productvariant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='cart_items') 
    quantity = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    objects = CartItemManager()
    Options= models.OneToOneField("products.ProductOption", verbose_name=_("آپشن ها"),null=True, blank=True, on_delete=models.CASCADE)

    @property
    def get_const(self):
        """محاسبه قیمت کل برای این آیتم"""
        return self.quantity * self.price

    @property
    def is_available(self):
        """بررسی موجود بودن محصول و واریانت"""
        return self.productvariant.stock >= self.quantity

    @property
    def remaining_stock(self):
        """مقدار باقیمانده از این محصول در انبار"""
        return self.productvariant.stock

    @property
    def product_name(self):
        """نام محصول به همراه واریانت"""
        return f"{self.product.title} - {self.productvariant.name}"

    def __str__(self):
        return f"{self.quantity}x {self.product.title} and variant {self.productvariant.id} in Cart {self.cart.id}"

    def get_dict(self):
        """تبدیل به دیکشنری برای استفاده در session یا API"""
        return {
            'id': self.id,
            'product_id': self.product.id,
            'variant_id': self.productvariant.id,
            'quantity': self.quantity,
            'price': self.price,
            'price': self.price,
            'options': self.Options.id if self.Options else None,
            'product_name': self.product_name
        }

    def add_one(self):
        """افزایش مقدار آیتم به میزان 1"""
        try:
            self.quantity = F('quantity') + 1
            self.save(update_fields=['quantity'])
            self.refresh_from_db()
            return self.quantity
        except Exception as e:
            return f"Error adding one to quantity: {e}"

    def decrease_one(self):
        """کاهش مقدار آیتم به میزان 1"""
        if self.quantity > 1:
            try:
                self.quantity = F('quantity') - 1
                self.save(update_fields=['quantity'])
                self.refresh_from_db()
                return self.quantity
            except Exception as e:
                return f"Error removing one from quantity: {e}"
        elif self.quantity <= 1:
            self.delete()
            
        else:
            return self.quantity

    def set_quantity(self, new_quantity):
        """تنظیم مقدار جدید برای آیتم"""
        if new_quantity > 0:
            try:
                self.quantity = new_quantity
                self.save(update_fields=['quantity'])
                return self.quantity
            except Exception as e:
                return f"Error setting quantity: {e}"
        return self.quantity

    def update_price(self):
        """بروزرسانی قیمت بر اساس قیمت فعلی محصول"""
        self.price = self.productvariant.price
        self.save(update_fields=['price'])
        return self.price

    def check_stock(self):
        """بررسی موجودی انبار برای این آیتم"""
        return self.productvariant.stock >= self.quantity

    def to_order_item(self, order):
        """تبدیل به آیتم سفارش"""
        from carts.models import OrderItem  # import here to avoid circular import
        return OrderItem.objects.create(
            order=order,
            product=self.product,
            productvariant=self.productvariant,
            quantity=self.quantity,
            price=self.price,
            Options=self.Options
        )
    
    

