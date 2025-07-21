from django.db import models
from users.models import User
from django_ckeditor_5.fields import CKEditor5Field
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Post(models.Model):
    title = models.CharField(_("عنوان"), max_length=255)
    slug = models.SlugField(_("اسلاگ"), unique=True)
    content = CKEditor5Field(_("محتوا"), config_name='default')
    image = models.ImageField(_("تصویر"), upload_to='post_images/')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name=_("نویسنده"))
    status = models.CharField(
        _("وضعیت"),
        max_length=50,
        choices=[
            ('draft', _('پیش‌نویس')),
            ('published', _('منتشرشده')),
            ('archived', _('آرشیوشده'))
        ]
    )
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    published_at = models.DateTimeField(_("تاریخ انتشار"), null=True, blank=True)
    updated_at = models.DateTimeField(_("آخرین به‌روزرسانی"), auto_now=True)
    available = models.BooleanField(_("فعال"), default=True)
    reading_time = models.PositiveIntegerField(_("زمان مطالعه"))
    history = AuditlogHistoryField(verbose_name=_('تاریخچه'), blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("پست")
        verbose_name_plural = _("پست‌ها")
        ordering = ['-published_at']


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_("پست"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_("کاربر"))
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    content = models.TextField(_("محتوا"))
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name=_("کامنت والد")
    )
    likes_count = models.IntegerField(_("تعداد لایک‌ها"), default=0)
    available = models.BooleanField(_("فعال"), default=True)
    history = AuditlogHistoryField(verbose_name=_('تاریخچه'), null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.content[:30]}"

    class Meta:
        verbose_name = _("کامنت")
        verbose_name_plural = _("کامنت‌ها")
        ordering = ['-created_at']


#برای ثبت تغییرات 
auditlog.register(Post)
auditlog.register(Comment)