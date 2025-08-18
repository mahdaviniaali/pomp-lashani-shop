from django.db import models
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth import get_user_model
from .manager import OrderManager, OrderItemManager, OrderShippingMethodManager
from django.db.models import F, Sum
from datetime import datetime
import shortuuid
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog



User = get_user_model()
def generate_invoice_number():
    date_part = datetime.now().strftime("%y%m%d")  
    random_part = shortuuid.ShortUUID().random(length=4)  
    return f"ORD-{date_part}-{random_part}"  







class CartNumber(models.Model):
    cart_name = models.CharField(_("نام کارت"), max_length=50)
    number = models.CharField(_("شماره کارت"), max_length=30, unique=True)
    bank_name = models.CharField(_("نام بانک"), max_length=20)
    available = models.BooleanField(_("فعال"), default=True)
    def __str__(self):
        return f"Cart #{self.cart_name} - Number: {self.number}"

    def save(self, *args, **kwargs):
        # اگر این کارت قرار است فعال شود (available=True)
        if self.available:
            # تمام کارت‌های دیگر را غیرفعال می‌کنیم
            CartNumber.objects.exclude(pk=self.pk).update(available=False)
        # اگر کارت غیرفعال شود و در حال حاضر تنها کارت فعال باشد، اجازه نمی‌دهیم
        elif not self.available and CartNumber.objects.filter(available=True).count() <= 1:
            raise ValueError("حداقل یک کارت باید فعال باشد!")
        super().save(*args, **kwargs)

        
    class Meta:
        verbose_name = _("شماره کارت")
        verbose_name_plural = _("شماره‌های کارت")

class PaymentMethod(models.TextChoices):
    GATEWAY = 'gateway', _('درگاه بانکی')
    MANUAL = 'manual', _('کارت به کارت')

class PaymentStatus(models.TextChoices):
    PENDING = 'pending', _('در انتظار پرداخت')
    SUCCESS = 'paid', _('پرداخت شده')
    FAILED = 'failed', _('ناموفق')
    CANCELED = 'canceled', _('لغو شده')
    WAITING_APPROVAL = 'waiting_approval', _('در انتظار تایید (کارت به کارت)')

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='payments', null=True, verbose_name=_("کاربر"))
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='payment', verbose_name=_("سفارش"))
    method = models.CharField(_("روش پرداخت"), max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(_("وضعیت پرداخت"), max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    amount = models.PositiveIntegerField(_("مبلغ"))
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    gateway_transaction_id = models.CharField(_("شناسه تراکنش درگاه"), max_length=100, blank=True, null=True)
    card_number = models.ForeignKey(CartNumber, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', verbose_name=_("شماره کارت"))
    receipt_image = models.ImageField(_("تصویر رسید"), upload_to='payments/receipts/', blank=True, null=True)
    description = models.TextField(_("توضیحات"), blank=True, null=True)
    history = AuditlogHistoryField(_("تاریخچه"), null=True, blank=True)
    def __str__(self):
        return f"Payment #{self.pk} - {self.get_method_display()}"

    class Meta:
        verbose_name = _("پرداخت")
        verbose_name_plural = _("پرداخت‌ها")

########
# مدل برای سفارشات
########

class Order (models.Model):
    #اطلاعات کاربر
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='order', null=True, verbose_name=_("کاربر"))
    user_fullname = models.CharField(_("نام مشتری"), max_length=50)
    user_phone_number = models.CharField(_("شماره تلفن"), max_length=13)
    user_email = models.EmailField(_("ایمیل"), max_length=254, blank=True, null=True)
    user_nationalcode = models.CharField(_("کد ملی"), max_length=50, blank=True, null=True)

    # اطلاعات خود سفارش
    order_number = models.CharField(_("شماره فاکتور"), max_length=18, unique=True) # باید ساخته بشه
    status = models.CharField(_("وضعیت سفارش"), max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    total_price = models.IntegerField(_("قیمت نهایی "), default=0) # گرفته و محاسبه میشه
    paid_price = models.IntegerField(_("مبلغ قابل پرداخت"), blank=True, null=True) # اینم باید محاسبه بشه
    payment_method = models.CharField(_("نحوه پرداخت"), max_length=20, choices=PaymentMethod.choices)
    description = models.TextField(_("توضیحات"), blank=True, null=True)
    created_at = models.DateTimeField(_("زمان تولید"), auto_now_add=True)
    update_at = models.DateTimeField(_("زمان اپدیت"), auto_now=True)

    # ادرس
    address_address = models.TextField(_("ادرس"))
    address_province = models.CharField(_("استان"), max_length=100)
    address_city = models.CharField(_("شهر"), max_length=100)
    address_postal_code = models.CharField(_("کد پستی"), max_length=20)

    history = AuditlogHistoryField(_("تاریخچه"), null=True, blank=True)

    
    objects = OrderManager()
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_invoice_number()
        super().save(*args, **kwargs)

    def get_total_price(self):
        return self.items.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
        
    def get_final_price(self):
        """محاسبه قیمت نهایی با در نظر گرفتن هزینه ارسال"""
        total = self.get_total_price()
        # اضافه کردن هزینه ارسال به قیمت نهایی اگر پس‌کرایه نباشد
        if self.shipping_method and not self.shipping_method.is_postpaid and self.shipping_method.price:
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

    def __str__(self):
        return f"Cart {self.id} - {self.user.username} - {self.user_phone_number} - {self.status}"

    class Meta:
        verbose_name = _("سفارش")
        verbose_name_plural = _("سفارش‌ها")

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_("سفارش"))
    product_name = models.CharField(_("نام محصول"), max_length=700)
    quantity = models.PositiveIntegerField(_("تعداد"))
    price = models.PositiveIntegerField(_("قیمت"))

    history = AuditlogHistoryField(_("تاریخچه"), null=True, blank=True)
    objects = OrderItemManager()
    def __str__(self):
        return f"{self.product_name} - {self.quantity} pcs"

    class Meta:
        verbose_name = _("آیتم سفارش")
        verbose_name_plural = _("آیتم‌های سفارش")

    def get_total_price(self):
        price = self.price if self.price is not None else 0
        quantity = self.quantity if self.quantity is not None else 0
        return price * quantity

class OrderItemOption(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='options', verbose_name=_("آیتم سفارش"))
    option_name = models.CharField(_("نام گزینه"), max_length=100)
    option_value = models.CharField(_("مقدار گزینه"), max_length=100)
    Price_increase = models.PositiveBigIntegerField(_("اضافه قیمت"))

    def __str__(self):
        return f"{self.option_name}: {self.option_value} for {self.order_item.product.name}"

    class Meta:
        verbose_name = _("گزینه آیتم سفارش")
        verbose_name_plural = _("گزینه‌های آیتم سفارش")

class OrderShippingMethod(models.Model):
    order = models.OneToOneField(Order, verbose_name=_("فاکتور متصل"), on_delete=models.CASCADE, related_name='shipping_method', null=True)
    name = models.CharField(max_length=50, verbose_name=_("نام روش ارسال"))
    price = models.PositiveIntegerField(verbose_name=_("هزینه ارسال (تومان)"), null=True, blank=True)
    is_postpaid = models.BooleanField(default=False, verbose_name=_("پس‌کرایه (هزینه با مشتری)"))

    objects = OrderShippingMethodManager()
    def __str__(self):
        return f"{self.name} - {self.price} تومان"
    
    def save(self, *args, **kwargs):
        # اگر قیمت مشخص نشده باشد، به صورت پیش‌ فرض پس‌کرایه است
        if self.price is None:
            self.is_postpaid = True
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("روش ارسال سفارش")
        verbose_name_plural = _("روش‌های ارسال سفارش")




########
#مدل برای هزینه های ارسال
########




class ShippingMethod(models.Model):
    """
    مدل پایه برای روش‌های ارسال (مثل تیپاکس، پست، اسنپ‌بکس).
    """
    name = models.CharField(max_length=50, unique=True, verbose_name=_("نام روش ارسال"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    active = models.BooleanField(default=True, verbose_name=_("فعال"))
    logo = models.ImageField(upload_to='shipping_logos/', null=True, blank=True, verbose_name=_("لوگو"))
    is_postpaid = models.BooleanField(default=False, verbose_name=_("پس‌کرایه (هزینه با مشتری)"))
    price = models.PositiveIntegerField(_("هزینه ارسال"), null=True, blank=True)

    class Meta:
        verbose_name = _("روش ارسال")
        verbose_name_plural = _("روش‌های ارسال")

    def __str__(self):
        return f"{self.name} - {self.price} تومان"
    
    def save(self, *args, **kwargs):
        # اگر قیمت مشخص نشده باشد، به صورت پیش‌ فرض پس‌کرایه است
        if self.price is None:
            self.is_postpaid = True
        super().save(*args, **kwargs)

class ShippingPrice(models.Model):
    """
    مدل برای تعیین هزینه‌های ارسال بر اساس وزن یا سایر شرایط.
    """
    method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.CASCADE,
        related_name='prices',
        verbose_name=_("روش ارسال")
    )
    base_price = models.PositiveIntegerField(verbose_name=_("هزینه پایه (تومان)"))
    max_weight_kg = models.PositiveIntegerField(verbose_name=_("حداکثر وزن مجاز (کیلوگرم)"))
    price_per_extra_kg = models.PositiveIntegerField(default=0, verbose_name=_("هزینه هر کیلوگرم اضافه (تومان)"))
    estimated_delivery_days = models.PositiveIntegerField(verbose_name=_("زمان تحویل تخمینی (روز)"))

    class Meta:
        verbose_name = _("هزینه ارسال")
        verbose_name_plural = _("هزینه‌های ارسال")
        ordering = ['method', 'max_weight_kg']

    def __str__(self):
        return f"{self.method.name} - تا {self.max_weight_kg} کیلوگرم"

class ShippingZone(models.Model):
    """
    مدل برای محدوده‌های جغرافیایی که روش ارسال در آن‌ها فعال است.
    """
    method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.CASCADE,
        related_name='zones',
        verbose_name="روش ارسال"
    )
    zone_name = models.CharField(max_length=100, verbose_name="نام محدوده")
    cities = models.TextField(verbose_name="شهرهای تحت پوشش")  # یا استفاده از مدل City جداگانه

    class Meta:
        verbose_name = "محدوده ارسال"
        verbose_name_plural = "محدوده‌های ارسال"

    def __str__(self):
        return f"{self.method.name} - {self.zone_name}"


    

#برای ثبت تغییرات 
auditlog.register(OrderItem)
auditlog.register(Order)
auditlog.register(Payment)




