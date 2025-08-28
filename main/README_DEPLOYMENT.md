# راهنمای استقرار پروژه روی سرور

## استقرار روی سرور با Passenger

برای استقرار پروژه روی سرور هاست که از Passenger استفاده می‌کند، باید فایل `passenger_wsgi.py` را در مسیر اصلی پروژه قرار دهید.

### مراحل استقرار

1. فایل `passenger_wsgi_server.py` را به `passenger_wsgi.py` تغییر نام دهید و در مسیر اصلی پروژه در سرور آپلود کنید:
   ```
   /home/waterris/pomp-lashani-shop/main/passenger_wsgi.py
   ```

2. اطمینان حاصل کنید که مسیر پروژه در فایل `passenger_wsgi.py` به درستی تنظیم شده باشد:
   ```python
   PROJECT_DIR = '/home/waterris/pomp-lashani-shop/main'
   ```

3. اطمینان حاصل کنید که تنظیمات محیطی Django به درستی تنظیم شده باشند. در صورت نیاز، متغیر محیطی `DJANGO_SETTINGS_MODULE` را در فایل `passenger_wsgi.py` تنظیم کنید:
   ```python
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
   ```

4. اطمینان حاصل کنید که تمام وابستگی‌های پروژه روی سرور نصب شده باشند:
   ```bash
   pip install -r requirements.txt
   ```

5. اطمینان حاصل کنید که دسترسی‌های لازم برای فایل‌ها و پوشه‌ها تنظیم شده باشند:
   ```bash
   chmod 755 /home/waterris/pomp-lashani-shop/main/passenger_wsgi.py
   ```

6. در صورت نیاز، سرور را ریستارت کنید.

### عیب‌یابی

اگر با خطای `FileNotFoundError: [Errno 2] No such file or directory: '/home/waterris/pomp-lashani-shop/main/passenger_wsgi.py'` مواجه شدید، به موارد زیر توجه کنید:

1. اطمینان حاصل کنید که فایل `passenger_wsgi.py` در مسیر صحیح قرار دارد.
2. اطمینان حاصل کنید که مسیر پروژه در فایل `passenger_wsgi.py` به درستی تنظیم شده است.
3. لاگ‌های سرور را بررسی کنید تا اطلاعات بیشتری در مورد خطا به دست آورید.
4. اطمینان حاصل کنید که دسترسی‌های لازم برای فایل‌ها و پوشه‌ها تنظیم شده باشند.

### نکات مهم

- در صورتی که از محیط مجازی Python استفاده می‌کنید، ممکن است نیاز باشد مسیر آن را در فایل `passenger_wsgi.py` تنظیم کنید.
- اطمینان حاصل کنید که نسخه Python مورد استفاده در سرور با نسخه مورد نیاز پروژه مطابقت دارد.
- در صورت نیاز به تغییر تنظیمات، فایل `passenger_wsgi.py` را ویرایش کنید و سرور را ریستارت کنید.