import os
import sys

# اضافه کردن مسیر پروژه به sys.path
PROJECT_DIR = '/home/waterris/pomp-lashani-shop/main'
sys.path.insert(0, PROJECT_DIR)

# اشاره به فایل wsgi.py اصلی پروژه
from main.wsgi import application