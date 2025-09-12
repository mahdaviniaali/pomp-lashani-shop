# راهنمای تست‌های پروژه جنگو

این پروژه شامل تست‌های جامع برای تمام بخش‌های اصلی است.

## 📋 فهرست تست‌ها

### 🏠 تست‌های Home App
- **HomeViewTest**: تست ویو صفحه اصلی
- **AboutUsViewTest**: تست ویو درباره ما
- **ConectUsViewTest**: تست ویو تماس با ما
- **UserAddressListViewTest**: تست ویو لیست آدرس کاربر
- **HomeModelsTest**: تست مدل‌های home

### 🛍️ تست‌های Products App
- **ProductListViewTest**: تست ویو لیست محصولات
- **ProductDetailViewTest**: تست ویو جزئیات محصول
- **PriceRangeViewTest**: تست ویو محدوده قیمت

### 👤 تست‌های Users App
- **UserModelTest**: تست مدل کاربر
- **AddressModelTest**: تست مدل آدرس
- **OTPModelTest**: تست مدل OTP
- **UserManagerTest**: تست مدیر کاربر
- **UserIntegrationTest**: تست‌های یکپارچه

### 🛒 تست‌های Common App
- **CartModelTest**: تست مدل سبد خرید
- **CartItemModelTest**: تست مدل آیتم سبد خرید

## 🚀 نحوه اجرای تست‌ها

### اجرای تمام تست‌ها (با تنظیمات تست)
```bash
# روش 1: استفاده از اسکریپت تست
python test_command.py

# روش 2: استفاده از اسکریپت جامع
python run_tests.py

# روش 3: دستور مستقیم با تنظیمات تست
DJANGO_SETTINGS_MODULE=main.settings.test python manage.py test
```

### اجرای تست‌ها با تنظیمات عادی (ممکن است خطا بدهد)
```bash
python manage.py test
```

### اجرای تست‌های خاص
```bash
python manage.py test home.tests.HomeViewTest
python manage.py test users.tests.UserModelTest
```

### اجرای تست‌ها با جزئیات
```bash
python manage.py test --verbosity=2
```

### اجرای تست‌های یک اپ خاص
```bash
python manage.py test home
python manage.py test products
python manage.py test users
```

## 📊 اجرای تست‌ها با پوشش کد

```bash
# نصب coverage
pip install coverage

# اجرای تست‌ها با پوشش کد
coverage run --source='.' manage.py test

# نمایش گزارش
coverage report

# تولید گزارش HTML
coverage html
```

## 🎯 استفاده از اسکریپت جامع

```bash
# اجرای تمام تست‌ها
python run_comprehensive_tests.py all

# اجرای تست‌های خاص
python run_comprehensive_tests.py specific

# اجرای تست‌ها با پوشش کد
python run_comprehensive_tests.py coverage
```

## 📝 نکات مهم

1. **پاک کردن کش**: تمام تست‌ها کش را پاک می‌کنند
2. **فایل‌های تست**: فایل‌های آپلود شده در تست‌ها پاک می‌شوند
3. **پایگاه داده**: از SQLite در حافظه استفاده می‌شود
4. **ایزوله بودن**: هر تست مستقل اجرا می‌شود

## 🔧 تنظیمات تست

فایل `test_config.py` شامل تنظیمات مخصوص تست است:
- پایگاه داده در حافظه
- کش محلی
- ایمیل در حافظه
- مسیرهای فایل تست

## 📈 انواع تست‌ها

### تست‌های واحد (Unit Tests)
- تست مدل‌ها
- تست متدها
- تست validation ها

### تست‌های یکپارچه (Integration Tests)
- تست تعامل بین مدل‌ها
- تست فرآیندهای کامل

### تست‌های ویو (View Tests)
- تست HTTP response ها
- تست context data
- تست authentication

## 🐛 عیب‌یابی

اگر تست‌ها ناموفق باشند:
1. بررسی کنید که تمام dependencies نصب شده باشند
2. مطمئن شوید که migrations اجرا شده باشند
3. بررسی کنید که فایل‌های تست syntax درستی داشته باشند

## 📚 منابع بیشتر

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
