from .base import *

CSRF_TRUSTED_ORIGINS=["https://astroedu.iau.org"]

try:
    from .local import *
except ImportError:
    pass
