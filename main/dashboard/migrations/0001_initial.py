# Generated manually for dashboard app

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cache_key', models.CharField(max_length=100, unique=True, verbose_name='کلید کش')),
                ('cache_data', models.JSONField(verbose_name='داده\u200cهای کش')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')),
                ('expires_at', models.DateTimeField(verbose_name='تاریخ انقضا')),
            ],
            options={
                'verbose_name': 'کش داشبورد',
                'verbose_name_plural': 'کش\u200cهای داشبورد',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='ReportLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(max_length=50, verbose_name='نوع گزارش')),
                ('generated_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ تولید')),
                ('parameters', models.JSONField(default=dict, verbose_name='پارامترهای گزارش')),
                ('file_path', models.CharField(blank=True, max_length=255, null=True, verbose_name='مسیر فایل')),
                ('generated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.user', verbose_name='تولید شده توسط')),
            ],
            options={
                'verbose_name': 'لاگ گزارش',
                'verbose_name_plural': 'لاگ\u200cهای گزارش',
                'ordering': ['-generated_at'],
            },
        ),
    ]
