import os

ENVIRONMENT = os.getenv('DEBUG', 'True')

if ENVIRONMENT == 'False':
    from .prod import *
elif ENVIRONMENT == 'True':
    from .dev import *
