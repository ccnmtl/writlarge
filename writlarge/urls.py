from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls.conf import path
from django.views.generic import TemplateView
from django.views.static import serve
from rest_framework import routers

from writlarge.main import views


admin.autodiscover()


auth_urls = url(r'^accounts/', include('django.contrib.auth.urls'))
if hasattr(settings, 'CAS_BASE'):
    auth_urls = url(r'^accounts/', include('djangowind.urls'))


router = routers.DefaultRouter()
router.register(r'site', views.LearningSiteViewSet, basename='site')
router.register(r'family', views.LearningSiteFamilyViewSet)
router.register(r'repository', views.ArchivalRepositoryViewSet)
router.register(r'place', views.PlaceViewSet)

urlpatterns = [
    url(r'^$', views.CoverView.as_view()),
    url(r'^api/', include(router.urls)),

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
    url(r'^edit/collection/(?P<pk>\d+)/$',
        views.ArchivalCollectionUpdateView.as_view(),
        name='collection-edit-view'),
    url(r'^delete/collection/(?P<parent>\d+)/(?P<pk>\d+)/$',
        views.ArchivalCollectionDeleteView.as_view(),
        name='collection-delete-view'),
    url(r'^view/collection/(?P<pk>\d+)/$',
        views.ArchivalCollectionDetailView.as_view(),
        name='collection-detail-view'),
    url(r'^collections/$', views.ArchivalCollectionListView.as_view(),
        name='archival-collections'),

    url(r'^suggest/collection/$',
        views.ArchivalCollectionSuggestView.as_view(),
        name='collection-suggest-view'),
    url(r'^suggest/collection/success/$',
        views.ArchivalCollectionSuggestSuccessView.as_view(),
        name='collection-suggest-success-view'),

    url(r'^add/footnote/(?P<parent>\d+)/$',
        views.FootnoteCreateView.as_view(),
        name='footnote-create-view'),
    url(r'^edit/footnote/(?P<parent>\d+)/(?P<pk>\d+)/$',
        views.FootnoteUpdateView.as_view(),
        name='footnote-edit-view'),
    url(r'^delete/footnote/(?P<parent>\d+)/(?P<pk>\d+)/$',
        views.FootnoteDeleteView.as_view(),
        name='footnote-delete-view'),

    url(r'^add/place/(?P<parent>\d+)/$',
        views.PlaceCreateView.as_view(),
        name='place-add-view'),
    url(r'^edit/place/(?P<parent>\d+)/(?P<pk>\d+)/$',
        views.PlaceUpdateView.as_view(),
        name='place-edit-view'),
    url(r'^delete/place/(?P<parent>\d+)/(?P<pk>\d+)/$',
        views.PlaceDeleteView.as_view(),
        name='place-delete-view'),

    url(r'^add/connection/(?P<parent>\d+)/$',
        views.ConnectionCreateView.as_view(),
        name='connection-add-view'),
    path(r'delete/connection/<int:parent>/<slug:type>/<int:pk>/',
         views.ConnectionDeleteView.as_view(),
         name='connection-delete-view'),

    url(r'^gallery/(?P<parent>\d+)/$',
        views.LearningSiteGalleryView.as_view(),
        name='site-gallery-view'),

    url(r'^date/display/$',
        views.DisplayDateView.as_view(),
        name='display-date-view'),

    url('^contact/', include('contactus.urls')),

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
