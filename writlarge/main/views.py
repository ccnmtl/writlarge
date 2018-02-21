from django.conf import settings
from django.forms.widgets import TextInput
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from rest_framework import viewsets

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import widgets

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


class PlaceDetailView(DetailView):
    model = Place


class PlaceUpdateView(LoginRequiredMixin, ModelFormWidgetMixin, UpdateView):
    model = Place
    fields = ['title', 'notes']
    widgets = {
        'title': TextInput
    }


class LearningSiteDetailView(DetailView):
    model = LearningSite


class LearningSiteUpdateView(LoginRequiredMixin, ModelFormWidgetMixin,
                             UpdateView):
    model = LearningSite
    fields = ['title', 'description', 'category', 'established', 'defunct',
              'instructional_level', 'founder',
              'tags', 'notes']
    widgets = {
        'title': widgets.TextInput,
        'category': widgets.CheckboxSelectMultiple,
        'established': widgets.SelectDateWidget(years=range(1500, 2018)),
        'defunct': widgets.SelectDateWidget(years=range(1500, 2018)),
        'instructional_level': widgets.TextInput
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
