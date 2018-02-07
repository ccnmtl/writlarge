from django.conf import settings
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from rest_framework import viewsets

from writlarge.main.models import LearningSite, ArchivalRepository
from writlarge.main.serializers import (
    ArchivalRepositorySerializer, LearningSiteSerializer)


# returns important setting information for all web pages.
# returns important setting information for all web pages.
def django_settings(request):
    whitelist = ['GOOGLE_ANALYTICS_ID', 'CAS_BASE']

    return {'settings': dict([(k, getattr(settings, k, None))
                              for k in whitelist])}


class CoverView(TemplateView):
    template_name = "main/cover.html"


class MapView(TemplateView):
    template_name = "main/map.html"


class SearchView(TemplateView):
    template_name = "main/search.html"


class LearningSiteDetailView(DetailView):
    model = LearningSite


class ArchivalRepositoryDetailView(DetailView):
    model = ArchivalRepository


"""
Rest API endpoints
"""


class ArchivalRepositoryViewSet(viewsets.ModelViewSet):
    queryset = ArchivalRepository.objects.all().order_by('-modified_at')
    serializer_class = ArchivalRepositorySerializer


class LearningSiteViewSet(viewsets.ModelViewSet):
    queryset = LearningSite.objects.all().order_by('-modified_at')
    serializer_class = LearningSiteSerializer
