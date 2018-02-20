from django.conf import settings
from django.forms.widgets import TextInput, DateInput, \
    CheckboxSelectMultiple, SelectDateWidget
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from rest_framework import viewsets

from writlarge.main.mixins import ModelFormWidgetMixin
from writlarge.main.models import LearningSite, ArchivalRepository, Place
from writlarge.main.serializers import (
    ArchivalRepositorySerializer, LearningSiteSerializer, PlaceSerializer)


# returns important setting information for all web pages.
# returns important setting information for all web pages.
def django_settings(request):
    whitelist = ['GOOGLE_MAP_API']

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


class LearningSiteUpdateView(ModelFormWidgetMixin, UpdateView):
    model = LearningSite
    fields = ['title', 'category', 'established',
              'defunct', 'notes', 'tags', 'verified']
    widgets = {
        'title': TextInput,
        'category': CheckboxSelectMultiple,
        'established': SelectDateWidget,
        'defunct': DateInput,
    }


class ArchivalRepositoryDetailView(DetailView):
    model = ArchivalRepository


class ArchivalRepositoryUpdateView(ModelFormWidgetMixin, UpdateView):
    model = ArchivalRepository

    fields = ['title', 'notes', 'tags', 'verified']
    widgets = {
        'title': TextInput
    }


"""
Rest API endpoints
"""


class ArchivalRepositoryViewSet(viewsets.ModelViewSet):
    queryset = ArchivalRepository.objects.all().order_by('-modified_at')
    serializer_class = ArchivalRepositorySerializer


class LearningSiteViewSet(viewsets.ModelViewSet):
    queryset = LearningSite.objects.all().order_by('-modified_at')
    serializer_class = LearningSiteSerializer


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all().order_by('-modified_at')
    serializer_class = PlaceSerializer
