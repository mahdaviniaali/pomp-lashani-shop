
from django.db import models
from users.models import User
# Create your models here.

class Notification(models.Model):
    # هر نوتیفیکیشن متعلق به یک کاربر است
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    # پیام و نوع نوتیفیکیشن
    message = models.TextField()
    type = models.CharField(max_length=50)
    # آیا نوتیفیکیشن خوانده شده است؟
    is_read = models.BooleanField(default=False)
    # زمان تحویل و ایجاد نوتیفیکیشن
    delivered_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=True)
    class Meta:
        verbose_name = 'نوتیفیکیشن'
        verbose_name_plural = 'نوتیفیکیشن‌ها'
        ordering = ['-created_at']