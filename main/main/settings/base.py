"""
Django base settings for main project.
"""

from pathlib import Path
import environ
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# مقداردهی اولیه django-environ
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])




# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    'formtools',
    'common.apps.CommonConfig',
    'home.apps.HomeConfig',
    'users.apps.UsersConfig',
    'otp_auth.apps.OtpAuthConfig',
    'products.apps.ProductsConfig',
    'carts.apps.CartsConfig',
    'payments.apps.PaymentsConfig',
    'blog.apps.BlogConfig',
    'cms.apps.CmsConfig',
    'notifications.apps.NotificationsConfig',
    'categories.apps.CategoriesConfig',
    'support.apps.SupportConfig',
    'discounts.apps.DiscountsConfig',
    'dashboard.apps.DashboardConfig',
    "django_ckeditor_5",
    'django_extensions',
    'taggit',
    'mptt',
    'auditlog',
    'debug_toolbar',
    'import_export',
    'django_admin_listfilter_dropdown',
    'rangefilter',
    'admin_auto_filters',
    'meta',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'main.middleware.GlobalRateLimitMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.global_context',
            ],
            'libraries': {
                'main_filters' : 'main.templatetags.global_filters',
            },
        },
    },
]



# Database
DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE"),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

WSGI_APPLICATION = 'main.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "assets")]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/users/login'

# Custom settings
ADMIN_PHONE = str(env("ADMIN_PHONE"))
SMSIR_API_KEY = str(env("SMSIR_API_KEY"))
SMSIR_LINE_NUMBER = str(env("SMSIR_LINE_NUMBER"))
SMSIR_VERIFY_TEMPLATE_ID = str(env("SMSIR_VERIFY_TEMPLATE_ID"))

# CKEditor 5 Configuration
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|",
            "bold", "italic", "underline", "|",
            "link", "imageUpload", "codeBlock", "mediaEmbed", "|",
            "bulletedList", "numberedList", "|",
            "blockQuote", "insertTable", "|",
            "undo", "redo"
        ],
        "language": "fa",
    }
}
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Rate limiting
GLOBAL_RATE_LIMIT = {
    'RATE_LIMIT': 100000,
    'TIME_WINDOW': 60,
}

# Jazzmin Configuration
JAZZMIN_SETTINGS = {
    "site_title": "پمپ‌شاپ",
    "site_header": "پمپ‌شاپ",
    "site_brand": "پمپ‌شاپ",
    "site_logo": None,
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "به پنل مدیریت پمپ‌شاپ خوش آمدید",
    "copyright": "پمپ‌شاپ",
    "search_model": ["auth.User", "products.Product"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "داشبورد", "url": "/dashboard/", "permissions": ["auth.view_user"]},
        {"name": "خانه", "url": "/", "new_window": True},
        {"model": "auth.User"},
        {"app": "products"},
    ],
    "usermenu_links": [
        {"name": "داشبورد", "url": "/dashboard/", "permissions": ["auth.view_user"]},
        {"model": "auth.user"}
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "products", "payments", "users"],
    "custom_links": {
        "products": [{
            "name": "داشبورد فروش",
            "url": "/dashboard/sales/",
            "icon": "fas fa-chart-line",
            "permissions": ["auth.view_user"]
        }]
    },
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "products.Product": "fas fa-box",
        "products.ProductVariant": "fas fa-cube",
        "payments.Order": "fas fa-shopping-cart",
        "payments.Payment": "fas fa-credit-card",
        "users.User": "fas fa-user",
        "blog.Post": "fas fa-blog",
        "dashboard.DashboardCache": "fas fa-database",
        "dashboard.ReportLog": "fas fa-file-alt",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "accent": "accent-teal",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-info",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}