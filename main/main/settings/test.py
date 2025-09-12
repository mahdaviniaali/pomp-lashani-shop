"""
تنظیمات تست برای پروژه جنگو
این فایل تنظیمات مخصوص اجرای تست‌ها را شامل می‌شود
"""

from .base import *
import os

# تنظیمات تست
DEBUG = False
TESTING = True

# غیرفعال کردن debug toolbar در تست‌ها
DEBUG_TOOLBAR_CONFIG = {
    'IS_RUNNING_TESTS': True,
}

# حذف debug toolbar از middleware در تست‌ها
MIDDLEWARE = [middleware for middleware in MIDDLEWARE 
              if middleware != 'debug_toolbar.middleware.DebugToolbarMiddleware']

# حذف debug toolbar از installed apps در تست‌ها
INSTALLED_APPS = [app for app in INSTALLED_APPS 
                  if app != 'debug_toolbar']

# پایگاه داده تست - استفاده از SQLite در حافظه
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# کش تست - استفاده از کش محلی
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ایمیل تست - استفاده از backend در حافظه
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# فایل‌های رسانه تست
MEDIA_ROOT = '/tmp/test_media/'
STATIC_ROOT = '/tmp/test_static/'

# غیرفعال کردن logging در تست‌ها
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# تنظیمات امنیتی برای تست
SECRET_KEY = 'test-secret-key-for-testing-only'
ALLOWED_HOSTS = ['*']

# غیرفعال کردن rate limiting در تست‌ها
GLOBAL_RATE_LIMIT = {
    'RATE_LIMIT': 1000000,  # محدودیت بالا برای تست
    'TIME_WINDOW': 1,
}

# تنظیمات SMS برای تست (مقادیر dummy)
SMSIR_API_KEY = 'test-api-key'
SMSIR_LINE_NUMBER = 'test-line-number'
SMSIR_VERIFY_TEMPLATE_ID = 'test-template-id'
ADMIN_PHONE = '09123456789'

# تنظیمات پرداخت برای تست
SANDBOX = True
MERCHANT = "test-merchant-id"

# غیرفعال کردن WhiteNoise در تست‌ها
MIDDLEWARE = [middleware for middleware in MIDDLEWARE 
              if middleware != 'whitenoise.middleware.WhiteNoiseMiddleware']

# تنظیمات PASSWORD_HASHERS برای سرعت بیشتر در تست‌ها
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# غیرفعال کردن migration در تست‌ها (اختیاری)
# MIGRATION_MODULES = {
#     'users': None,
#     'products': None,
#     'home': None,
#     'common': None,
# }
