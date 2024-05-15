from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.static import serve
from rest_framework import routers
from django_cas_ng import views as cas_views

from writlarge.main import views


admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'site', views.LearningSiteViewSet, basename='site')
router.register(r'family', views.LearningSiteFamilyViewSet)
router.register(r'repository', views.ArchivalRepositoryViewSet)
router.register(r'place', views.PlaceViewSet)

urlpatterns = [
    path('', views.CoverView.as_view()),
    path('api/', include(router.urls)),

    path('accounts/', include('django.contrib.auth.urls')),

    path('cas/login', cas_views.LoginView.as_view(),
         name='cas_ng_login'),
    path('cas/logout', cas_views.LogoutView.as_view(),
         name='cas_ng_logout'),

    path('map/', views.MapView.as_view(), name='map-view'),

    path('search/', views.SearchView.as_view(), name='search-view'),

    re_path(r'^view/(?P<pk>\d+)/$', views.LearningSiteDetailView.as_view(),
            name='site-detail-view'),
    re_path(r'^edit/(?P<pk>\d+)/$', views.LearningSiteUpdateView.as_view(),
            name='site-update-view'),
    re_path(r'^delete/(?P<pk>\d+)/$',
            views.LearningSiteDeleteView.as_view(),
            name='site-delete-view'),

    re_path(r'^add/photo/(?P<parent>\d+)/$',
            views.DigitalObjectCreateView.as_view(),
            name='digital-object-create-view'),
    re_path(r'^edit/photo/(?P<pk>\d+)/$',
            views.DigitalObjectUpdateView.as_view(),
            name='digital-object-edit-view'),
    re_path(r'^delete/photo/(?P<pk>\d+)/$',
            views.DigitalObjectDeleteView.as_view(),
            name='digital-object-delete-view'),

    re_path(r'^link/collection/(?P<parent>\d+)/$',
            views.ArchivalCollectionLinkView.as_view(),
            name='collection-link-view'),
    re_path(r'^unlink/collection/(?P<parent>\d+)/(?P<pk>\d+)/$',
            views.ArchivalCollectionUnlinkView.as_view(),
            name='collection-unlink-view'),
    re_path(r'^create/collection/(?P<parent>\d+)/$',
            views.ArchivalCollectionCreateView.as_view(),
            name='collection-create-view'),
    re_path(r'^edit/collection/(?P<parent>\d+)/(?P<pk>\d+)/$',
            views.ArchivalCollectionUpdateView.as_view(),
            name='collection-edit-view'),
    re_path(r'^edit/collection/(?P<pk>\d+)/$',
            views.ArchivalCollectionUpdateView.as_view(),
            name='collection-edit-view'),
    re_path(r'^delete/collection/(?P<parent>\d+)/(?P<pk>\d+)/$',
            views.ArchivalCollectionDeleteView.as_view(),
            name='collection-delete-view'),
    re_path(r'^view/collection/(?P<pk>\d+)/$',
            views.ArchivalCollectionDetailView.as_view(),
            name='collection-detail-view'),
    path('collections/', views.ArchivalCollectionListView.as_view(),
         name='archival-collections'),

    path('suggest/collection/',
         views.ArchivalCollectionSuggestView.as_view(),
         name='collection-suggest-view'),
    path('suggest/collection/success/',
         views.ArchivalCollectionSuggestSuccessView.as_view(),
         name='collection-suggest-success-view'),

    re_path(r'^add/footnote/(?P<parent>\d+)/$',
            views.FootnoteCreateView.as_view(),
            name='footnote-create-view'),
    re_path(r'^edit/footnote/(?P<parent>\d+)/(?P<pk>\d+)/$',
            views.FootnoteUpdateView.as_view(),
            name='footnote-edit-view'),
    re_path(r'^delete/footnote/(?P<parent>\d+)/(?P<pk>\d+)/$',
            views.FootnoteDeleteView.as_view(),
            name='footnote-delete-view'),

    re_path(r'^add/place/(?P<parent>\d+)/$',
            views.PlaceCreateView.as_view(),
            name='place-add-view'),
    re_path(r'^edit/place/(?P<parent>\d+)/(?P<pk>\d+)/$',
            views.PlaceUpdateView.as_view(),
            name='place-edit-view'),
    re_path(r'^delete/place/(?P<parent>\d+)/(?P<pk>\d+)/$',
            views.PlaceDeleteView.as_view(),
            name='place-delete-view'),

    re_path(r'^add/connection/(?P<parent>\d+)/$',
            views.ConnectionCreateView.as_view(),
            name='connection-add-view'),
    path('delete/connection/<int:parent>/<slug:type>/<int:pk>/',
         views.ConnectionDeleteView.as_view(),
         name='connection-delete-view'),

    re_path(r'^gallery/(?P<parent>\d+)/$',
            views.LearningSiteGalleryView.as_view(),
            name='site-gallery-view'),

    path('date/display/',
         views.DisplayDateView.as_view(),
         name='display-date-view'),

    path('contact/', include('contactus.urls')),

    path('admin/', admin.site.urls),
    path('_impersonate/', include('impersonate.urls')),
    path('stats/', TemplateView.as_view(template_name="stats.html")),
    re_path(r'smoketest/', include('smoketest.urls')),
    re_path(r'^uploads/(?P<path>.*)$',
            serve, {'document_root': settings.MEDIA_ROOT}),
    path('lti/', include('lti_provider.urls'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
