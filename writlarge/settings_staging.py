# flake8: noqa
from django.conf import settings
from writlarge.settings_shared import *
from ccnmtlsettings.staging import common
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

locals().update(
    common(
        project=project,
        base=base,
        STATIC_ROOT=STATIC_ROOT,
        INSTALLED_APPS=INSTALLED_APPS,
# if you use cloudfront:
#        cloudfront="justtheidhere",
# if you don't use S3/cloudfront at all:
#       s3static=False,
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

try:
    from writlarge.local_settings import *
except ImportError:
    pass

if hasattr(settings, 'SENTRY_DSN'):
    sentry_sdk.init(
        dsn=SENTRY_DSN,  # noqa: F405
        integrations=[DjangoIntegration()],
        debug=True,
    )
