# Generated by Django 5.1.4 on 2025-07-22 16:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ['-id'], 'verbose_name': 'آدرس', 'verbose_name_plural': 'آدرس\u200cها'},
        ),
        migrations.AlterModelOptions(
            name='otp',
            options={'ordering': ['-created_at'], 'verbose_name': 'رمز یکبار مصرف', 'verbose_name_plural': 'رمزهای یکبار مصرف'},
        ),
        migrations.AlterField(
            model_name='address',
            name='address',
            field=models.TextField(verbose_name='آدرس'),
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(max_length=100, verbose_name='شهر'),
        ),
        migrations.AlterField(
            model_name='address',
            name='is_default',
            field=models.BooleanField(default=False, verbose_name='آدرس پیش\u200cفرض'),
        ),
        migrations.AlterField(
            model_name='address',
            name='postal_code',
            field=models.CharField(max_length=20, verbose_name='کد پستی'),
        ),
        migrations.AlterField(
            model_name='address',
            name='province',
            field=models.CharField(max_length=100, verbose_name='استان'),
        ),
        migrations.AlterField(
            model_name='address',
            name='title',
            field=models.CharField(max_length=100, verbose_name='عنوان'),
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='otp',
            name='code',
            field=models.CharField(max_length=6, verbose_name='کد'),
        ),
        migrations.AlterField(
            model_name='otp',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AlterField(
            model_name='otp',
            name='expires_at',
            field=models.DateTimeField(verbose_name='تاریخ انقضا'),
        ),
        migrations.AlterField(
            model_name='otp',
            name='phone_number',
            field=models.CharField(max_length=15, unique=True, verbose_name='شماره تلفن'),
        ),
    ]
