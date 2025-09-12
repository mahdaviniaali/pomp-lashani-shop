#!/usr/bin/env python
"""
اسکریپت ساده برای اجرای تست‌ها با تنظیمات مخصوص تست
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """اجرای تست‌ها با تنظیمات مخصوص تست"""
    
    # تنظیم متغیر محیطی برای استفاده از تنظیمات تست
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings.test')
    
    # راه‌اندازی Django
    django.setup()
    
    print("🧪 شروع اجرای تست‌ها با تنظیمات مخصوص تست...")
    print("=" * 60)
    
    # اجرای تست‌ها
    try:
        execute_from_command_line(['manage.py', 'test', '--verbosity=2'])
        print("\n✅ تمام تست‌ها با موفقیت اجرا شدند!")
    except SystemExit as e:
        if e.code == 0:
            print("\n✅ تمام تست‌ها با موفقیت اجرا شدند!")
        else:
            print(f"\n❌ برخی تست‌ها ناموفق بودند. کد خروج: {e.code}")
            sys.exit(e.code)
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
