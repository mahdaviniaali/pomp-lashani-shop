#!/usr/bin/env python
"""
دستور ساده برای اجرای تست‌ها
استفاده: python test_command.py
"""

import os
import sys

# تنظیم متغیر محیطی برای استفاده از تنظیمات تست
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings.test')

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'test', '--verbosity=2'])
