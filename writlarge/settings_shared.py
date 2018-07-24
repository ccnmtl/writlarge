# flake8: noqa
# Django settings for writlarge project.
import os.path
import platform
import sys
from ccnmtlsettings.shared import common


project = 'writlarge'
base = os.path.dirname(__file__)

locals().update(common(project=project, base=base))


if platform.linux_distribution()[0] == 'Ubuntu':
    if platform.linux_distribution()[1] == '16.04':
        # 15.04 and later need this set, but it breaks
        # on trusty.
        # yeah, it's not really going to work on non-Ubuntu
        # systems either, but I don't know a good way to
        # check for the specific issue. Anyone not running
        # ubuntu will just need to set this to the
        # appropriate value in their local_settings.py
        SPATIALITE_LIBRARY_PATH = 'mod_spatialite'
    elif platform.linux_distribution()[1] == '18.04':
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
    'infranil',
    'writlarge.main',
    'taggit',
    'django.contrib.gis',
    'rest_framework',
    'lti_provider',
    'edtf',
    'debug_toolbar',
    'contactus'
]

LOGIN_REDIRECT_URL = "/"

TEMPLATES[0]['OPTIONS']['context_processors'].append(  # noqa
    'django.template.context_processors.csrf')
TEMPLATES[0]['OPTIONS']['context_processors'].append(  # noqa
    'writlarge.main.views.django_settings')

MIDDLEWARE = [
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'waffle.middleware.WaffleMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'writlarge.main.middleware.WhodidMiddleware'
]


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'PAGINATE_BY': 15,
    'DATETIME_FORMAT': '%m/%d/%y %I:%M %p'
}


AUTHENTICATION_BACKENDS = [
    'djangowind.auth.SAMLAuthBackend',
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


WIND_AFFIL_HANDLERS = [
    'writlarge.main.auth.EditorMapper',
    'djangowind.auth.StaffMapper',
    'djangowind.auth.SuperuserMapper'
]

CONTACT_US_EMAIL = 'ctl-writlarge@columbia.edu'
