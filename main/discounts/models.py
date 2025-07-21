
from django.db import models
from products.models import Product
# Create your models here.

class DiscountCode(models.Model):
    # کد تخفیف و درصد یا مبلغ تخفیف
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.FloatField()
    discount_amount = models.IntegerField()
    # حداکثر تعداد استفاده و تعداد استفاده‌شده
    max_usage = models.IntegerField()
    used_count = models.IntegerField(default=0)
    # زمان انقضای کد تخفیف
    expires_at = models.DateTimeField()
    # محصولات قابل اعمال کد تخفیف
    applicable_products = models.ManyToManyField(Product, blank=True, related_name='discount_codes')
    created_at = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=True)
    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کدهای تخفیف'
        ordering = ['-expires_at']