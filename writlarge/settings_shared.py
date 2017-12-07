# flake8: noqa
# Django settings for writlarge project.
import os.path
import platform
import sys
from ccnmtlsettings.shared import common


project = 'writlarge'
base = os.path.dirname(__file__)

locals().update(common(project=project, base=base))


if platform.linux_distribution()[1] == '16.04':
    # 15.04 and later need this set, but it breaks
    # on trusty.
    # yeah, it's not really going to work on non-Ubuntu
    # systems either, but I don't know a good way to
    # check for the specific issue. Anyone not running
    # ubuntu will just need to set this to the
    # appropriate value in their local_settings.py
    SPATIALITE_LIBRARY_PATH = 'mod_spatialite'


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'writlarge',
        'HOST': '',
        'PORT': 5432,
        'USER': '',
        'PASSWORD': '',
        'ATOMIC_REQUESTS': True,
    }
}

if ('test' in sys.argv or 'jenkins' in sys.argv or 'validate' in sys.argv
        or 'check' in sys.argv):
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.spatialite',
            'NAME': ':memory:',
            'HOST': '',
            'PORT': '',
            'USER': '',
            'PASSWORD': '',
            'ATOMIC_REQUESTS': True,
        }
    }

PROJECT_APPS = [
    'writlarge.main',
]

USE_TZ = True

INSTALLED_APPS += [  # noqa
    'bootstrap4',
    'infranil',
    'writlarge.main',
]

LOGIN_REDIRECT_URL = "/"

TEMPLATES[0]['OPTIONS']['context_processors'].append(  # noqa
    'django.template.context_processors.csrf')
TEMPLATES[0]['OPTIONS']['context_processors'].append(  # noqa
    'writlarge.main.views.django_settings')

MIDDLEWARE_CLASSES += [  # noqa
    'django.middleware.csrf.CsrfViewMiddleware',
    'audit_log.middleware.UserLoggingMiddleware',
    'reversion.middleware.RevisionMiddleware'
]
