"""
تنظیمات تست برای پروژه جنگو
"""

# تنظیمات پایگاه داده تست
TEST_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# تنظیمات کش تست
TEST_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# تنظیمات ایمیل تست
TEST_EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# تنظیمات فایل تست
TEST_MEDIA_ROOT = '/tmp/test_media/'
TEST_STATIC_ROOT = '/tmp/test_static/'
