from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    password_change,
    password_change_done, password_reset, password_reset_done,
    password_reset_confirm,
    password_reset_complete)
from django.views.generic import TemplateView
from django.views.static import serve

from writlarge.main import views


admin.autodiscover()


auth_urls = url(r'^accounts/', include('django.contrib.auth.urls'))
if hasattr(settings, 'CAS_BASE'):
    auth_urls = url(r'^accounts/', include('djangowind.urls'))


urlpatterns = [
    url(r'^$', views.IndexView.as_view()),

    url(r'^accounts/login/$', views.LoginView.as_view()),
    url(r'^accounts/logout/$', views.LogoutView.as_view()),

    # password change & reset. overriding to gate them.
    url(r'^accounts/password_change/$',
        login_required(password_change),
        name='password_change'),
    url(r'^accounts/password_change/done/$',
        login_required(password_change_done),
        name='password_change_done'),
    url(r'^password/reset/$',
        password_reset,
        name='password_reset'),
    url(r'^password/reset/done/$', password_reset_done,
        name='password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^password/reset/complete/$',
        password_reset_complete, name='password_reset_complete'),

    auth_urls,

    url(r'^admin/', include(admin.site.urls)),
    url(r'^_impersonate/', include('impersonate.urls')),
    url(r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    url(r'smoketest/', include('smoketest.urls')),
    url(r'infranil/', include('infranil.urls')),
    url(r'^uploads/(?P<path>.*)$',
        serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
