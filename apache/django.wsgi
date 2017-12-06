import os, sys, site

# enable the virtualenv
site.addsitedir('/var/www/writlarge/writlarge/ve/lib/python2.7/site-packages')

# paths we might need to pick up the project's settings
sys.path.append('/var/www/writlarge/writlarge/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'writlarge.settings_production'

import django
django.setup()

import django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
