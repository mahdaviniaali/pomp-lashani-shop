#!/usr/bin/env python
"""
اسکریپت جامع برای اجرای تمام تست‌های پروژه جنگو
این اسکریپت تمام تست‌های نوشته شده را اجرا می‌کند و گزارش کاملی ارائه می‌دهد
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line

def setup_django():
    """تنظیم Django برای اجرای تست‌ها"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings.test')
    django.setup()

def run_all_tests():
    """اجرای تمام تست‌های پروژه"""
    print("🚀 شروع اجرای تست‌های جامع پروژه...")
    print("=" * 60)
    
    # لیست تمام اپ‌های پروژه که تست دارند
    test_apps = [
        'home',
        'products', 
        'users',
        'common',
        'categories',
        'blog',
        'carts',
        'payments',
        'notifications',
        'support',
        'discounts',
        'otp_auth',
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for app in test_apps:
        print(f"\n📱 تست‌های اپ {app.upper()}:")
        print("-" * 40)
        
        try:
            # اجرای تست‌های هر اپ
            result = execute_from_command_line([
                'manage.py', 'test', app, '--verbosity=2'
            ])
            
            # اگر تست‌ها موفق باشند
            print(f"✅ تست‌های {app} با موفقیت اجرا شدند")
            
        except SystemExit as e:
            if e.code == 0:
                print(f"✅ تست‌های {app} با موفقیت اجرا شدند")
            else:
                print(f"❌ خطا در تست‌های {app}")
                total_errors += 1
        except Exception as e:
            print(f"❌ خطای غیرمنتظره در تست‌های {app}: {e}")
            total_errors += 1
    
    print("\n" + "=" * 60)
    print("📊 خلاصه نتایج:")
    print(f"✅ تست‌های موفق: {len(test_apps) - total_errors}")
    print(f"❌ تست‌های ناموفق: {total_errors}")
    print("=" * 60)

def run_specific_tests():
    """اجرای تست‌های خاص"""
    print("🎯 اجرای تست‌های خاص...")
    
    # تست‌های مدل‌ها
    print("\n📋 تست‌های مدل‌ها:")
    execute_from_command_line(['manage.py', 'test', 'home.tests.HomeModelsTest', '--verbosity=2'])
    execute_from_command_line(['manage.py', 'test', 'users.tests.UserModelTest', '--verbosity=2'])
    execute_from_command_line(['manage.py', 'test', 'common.tests.CartModelTest', '--verbosity=2'])
    
    # تست‌های ویو‌ها
    print("\n🖥️ تست‌های ویو‌ها:")
    execute_from_command_line(['manage.py', 'test', 'home.tests.HomeViewTest', '--verbosity=2'])
    execute_from_command_line(['manage.py', 'test', 'products.tests.ProductListViewTest', '--verbosity=2'])
    
    # تست‌های یکپارچه
    print("\n🔗 تست‌های یکپارچه:")
    execute_from_command_line(['manage.py', 'test', 'users.tests.UserIntegrationTest', '--verbosity=2'])

def run_coverage_tests():
    """اجرای تست‌ها با پوشش کد"""
    try:
        import coverage
        print("📊 اجرای تست‌ها با پوشش کد...")
        
        # شروع پوشش کد
        cov = coverage.Coverage()
        cov.start()
        
        # اجرای تمام تست‌ها
        execute_from_command_line(['manage.py', 'test', '--verbosity=2'])
        
        # توقف پوشش کد
        cov.stop()
        cov.save()
        
        # گزارش پوشش کد
        print("\n📈 گزارش پوشش کد:")
        cov.report()
        
        # تولید گزارش HTML
        cov.html_report(directory='htmlcov')
        print("\n📁 گزارش HTML در پوشه htmlcov/ ذخیره شد")
        
    except ImportError:
        print("⚠️ پکیج coverage نصب نشده است. برای نصب: pip install coverage")

def main():
    """تابع اصلی"""
    setup_django()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'all':
            run_all_tests()
        elif command == 'specific':
            run_specific_tests()
        elif command == 'coverage':
            run_coverage_tests()
        else:
            print("❌ دستور نامعتبر. دستورات موجود:")
            print("  python run_comprehensive_tests.py all      - اجرای تمام تست‌ها")
            print("  python run_comprehensive_tests.py specific - اجرای تست‌های خاص")
            print("  python run_comprehensive_tests.py coverage - اجرای تست‌ها با پوشش کد")
    else:
        print("🎯 اجرای تست‌های پیش‌فرض...")
        run_all_tests()

if __name__ == '__main__':
    main()
