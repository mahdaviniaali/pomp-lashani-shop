from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardCache(models.Model):
    """مدل برای کش کردن داده‌های داشبورد"""
    cache_key = models.CharField(_("کلید کش"), max_length=100, unique=True)
    cache_data = models.JSONField(_("داده‌های کش"))
    created_at = models.DateTimeField(_("تاریخ ایجاد"), auto_now_add=True)
    updated_at = models.DateTimeField(_("آخرین بروزرسانی"), auto_now=True)
    expires_at = models.DateTimeField(_("تاریخ انقضا"))

    class Meta:
        verbose_name = _("کش داشبورد")
        verbose_name_plural = _("کش‌های داشبورد")
        ordering = ['-updated_at']

    def __str__(self):
        return f"Cache: {self.cache_key}"


class ReportLog(models.Model):
    """مدل برای ثبت گزارشات تولید شده"""
    report_type = models.CharField(_("نوع گزارش"), max_length=50)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_("تولید شده توسط"))
    generated_at = models.DateTimeField(_("تاریخ تولید"), auto_now_add=True)
    parameters = models.JSONField(_("پارامترهای گزارش"), default=dict)
    file_path = models.CharField(_("مسیر فایل"), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _("لاگ گزارش")
        verbose_name_plural = _("لاگ‌های گزارش")
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.report_type} - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"