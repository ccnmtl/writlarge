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
from rest_framework import routers

from writlarge.main import views


admin.autodiscover()


auth_urls = url(r'^accounts/', include('django.contrib.auth.urls'))
if hasattr(settings, 'CAS_BASE'):
    auth_urls = url(r'^accounts/', include('djangowind.urls'))


router = routers.DefaultRouter()
router.register(r'site', views.LearningSiteViewSet)
router.register(r'repository', views.ArchivalRepositoryViewSet)

urlpatterns = [
    url(r'^$', views.CoverView.as_view()),
    url(r'^api/', include(router.urls)),

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

    url(r'^map/$', views.MapView.as_view(), name='map-view'),
    url(r'^search/$', views.SearchView.as_view(), name='search-view'),
    url(r'^view/(?P<pk>\d+)/$', views.LearningSiteDetailView.as_view(),
        name='site-detail-view'),
    url(r'^edit/(?P<pk>\d+)/$', views.LearningSiteUpdateView.as_view(),
        name='site-update-view'),
    url(r'^delete/(?P<pk>\d+)/$',
        views.LearningSiteDeleteView.as_view(),
        name='site-delete-view'),


    url(r'^add/photo/(?P<parent>\d+)/$',
        views.DigitalObjectCreateView.as_view(),
        name='digital-object-create-view'),
    url(r'^edit/photo/(?P<pk>\d+)/$',
        views.DigitalObjectUpdateView.as_view(),
        name='digital-object-edit-view'),
    url(r'^delete/photo/(?P<pk>\d+)/$',
        views.DigitalObjectDeleteView.as_view(),
        name='digital-object-delete-view'),

    url(r'^link/collection/(?P<parent>\d+)/$',
        views.ArchivalCollectionLinkView.as_view(),
        name='collection-link-view'),
    url(r'^unlink/collection/(?P<parent>\d+)/(?P<pk>\d+)/$',
        views.ArchivalCollectionUnlinkView.as_view(),
        name='collection-unlink-view'),
    url(r'^create/collection/(?P<parent>\d+)/$',
        views.ArchivalCollectionCreateView.as_view(),
        name='collection-create-view'),
    url(r'^edit/collection/(?P<parent>\d+)/(?P<pk>\d+)/$',
        views.ArchivalCollectionUpdateView.as_view(),
        name='collection-edit-view'),
    url(r'^delete/collection/(?P<parent>\d+)/(?P<pk>\d+)/$',
        views.ArchivalCollectionDeleteView.as_view(),
        name='collection-delete-view'),

    url(r'^add/footnote/(?P<parent>\d+)/$',
        views.FootnoteCreateView.as_view(),
        name='footnote-create-view'),
    url(r'^edit/footnote/(?P<parent>\d+)/(?P<pk>\d+)/$',
        views.FootnoteUpdateView.as_view(),
        name='footnote-edit-view'),
    url(r'^delete/footnote/(?P<parent>\d+)/(?P<pk>\d+)/$',
        views.FootnoteDeleteView.as_view(),
        name='footnote-delete-view'),

    url(r'^gallery/(?P<parent>\d+)/$',
        views.LearningSiteGalleryView.as_view(),
        name='site-gallery-view'),

    url(r'^date/display/$',
        views.DisplayDateView.as_view(),
        name='display-date-view'),

    url(r'^admin/', admin.site.urls),
    url(r'^_impersonate/', include('impersonate.urls')),
    url(r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    url(r'smoketest/', include('smoketest.urls')),
    url(r'infranil/', include('infranil.urls')),
    url(r'^uploads/(?P<path>.*)$',
        serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^lti/', include('lti_provider.urls'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
