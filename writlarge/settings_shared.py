# flake8: noqa
# Django settings for writlarge project.
import os.path
import platform
import sys
from ctlsettings.shared import common


project = 'writlarge'
base = os.path.dirname(__file__)

locals().update(common(project=project, base=base))

if hasattr(platform, "linux_distribution") and \
        platform.linux_distribution()[0] == 'Ubuntu':
    if platform.linux_distribution()[1] == '18.04':
        # On Debian testing/buster, I had to do the following:
        # * Install the sqlite3 and libsqlite3-mod-spatialite packages.
        # * Add the following to writlarge/local_settings.py:
        # SPATIALITE_LIBRARY_PATH =
        # '/usr/lib/x86_64-linux-gnu/mod_spatialite.so' I think the
        # django docs might be slightly out of date here, or just not
        # cover all the cases.
        #
        # I've found that Ubuntu 18.04 also works with this full path
        # to the library file, but not 'mod_spatialite'. I'll raise
        # this issue with Django.
        SPATIALITE_LIBRARY_PATH = '/usr/lib/x86_64-linux-gnu/mod_spatialite.so'


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
    'writlarge.main',
    'taggit',
    'django.contrib.gis',
    'rest_framework',
    'lti_provider',
    'edtf',
    'contactus',
    'django_markwhat',
]

LOGIN_REDIRECT_URL = "/"

TEMPLATES[0]['OPTIONS']['context_processors'].append(
    'django.template.context_processors.csrf')
TEMPLATES[0]['OPTIONS']['context_processors'].append(
    'writlarge.main.views.django_settings')

MIDDLEWARE = [
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'writlarge.main.middleware.WhodidMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'PAGINATE_BY': 15,
    'DATETIME_FORMAT': '%m/%d/%y %I:%M %p'
}


AUTHENTICATION_BACKENDS = [
    'django_cas_ng.backends.CASBackend',
    'django.contrib.auth.backends.ModelBackend',
    'lti_provider.auth.LTIBackend'
]


LTI_TOOL_CONFIGURATION = {
    'title': 'Writ Large',
    'description': 'Discover the Hidden Histories of New York City\'s '
    ' Teaching and Learning Communities',
    'launch_url': 'lti/',
    'embed_url': '',
    'embed_icon_url': '',
    'embed_tool_id': '',
    'landing_url': '{}://{}/map/',
    'course_aware': False,
    'navigation': True,
    'new_tab': True,
    'frame_width': 1024,
    'frame_height': 1024
}


CAS_AFFILIATIONS_HANDLERS = [
    'writlarge.main.auth.EditorMapper',
]

CONTACT_US_EMAIL = 'ctl-writlarge@columbia.edu'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'writlarge.main.utils.IsEditorOrAnonReadOnly'
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'writlarge.main.utils.BrowsableAPIRendererNoForms'
    ),
    'PAGINATE_BY': 15,
    'DATETIME_FORMAT': '%m/%d/%y %I:%M %p',
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 15,
}

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
