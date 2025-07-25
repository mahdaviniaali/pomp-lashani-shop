from .base import *

# SECURITY WARNING: don't run with debug turned on in production!


DEBUG=True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Debug Toolbar
INTERNAL_IPS = ['127.0.0.1']
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}

# Email settings (برای توسعه)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Additional local apps
INSTALLED_APPS += [
    'django_browser_reload',
]

# Sandbox payment
SANDBOX = True
MERCHANT = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'myapp': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}



# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
