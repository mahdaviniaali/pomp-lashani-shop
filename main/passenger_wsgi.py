import os
import sys

# اضافه کردن مسیر پروژه به sys.path
sys.path.insert(0, os.path.dirname(__file__))

# اشاره به فایل wsgi.py اصلی پروژه
from main.wsgi import application