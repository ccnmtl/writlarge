import sys
from django.conf import settings
from writlarge.settings_shared import *  # noqa: F403
from ctlsettings.staging import common
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

locals().update(
    common(
        project=project,  # noqa: F405
        base=base,  # noqa: F405
        STATIC_ROOT=STATIC_ROOT,  # noqa: F405
        INSTALLED_APPS=INSTALLED_APPS,  # noqa: F405
        s3prefix="ccnmtl",
    ))

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'writlarge',
        'HOST': '',
        'PORT': 6432,
        'USER': '',
        'PASSWORD': '',
    }
}

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication'
    ],
}

try:
    from writlarge.local_settings import *  # noqa: F403
except ImportError:
    pass

if ('migrate' not in sys.argv) and \
   ('collectstatic' not in sys.argv) and \
   hasattr(settings, 'SENTRY_DSN'):
    sentry_sdk.init(
        dsn=SENTRY_DSN,  # noqa: F405
        integrations=[DjangoIntegration()],
        debug=True,
    )
