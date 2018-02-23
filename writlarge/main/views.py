from django.conf import settings
from django.forms import widgets
from django.forms.widgets import TextInput
from django.urls.base import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.list import ListView
from rest_framework import viewsets

from writlarge.main.mixins import (
    LearningSiteParamMixin, LearningSiteRelatedMixin,
    ModelFormWidgetMixin, LoggedInEditorMixin)
from writlarge.main.models import LearningSite, ArchivalRepository, Place, \
    DigitalObject
from writlarge.main.serializers import (
    ArchivalRepositorySerializer, LearningSiteSerializer, PlaceSerializer)


# returns important setting information for all web pages.
def django_settings(request):
    whitelist = ['GOOGLE_MAP_API']
    return {
        'is_editor': (request.user.groups and
                      request.user.groups.filter(name='Editor').exists()),
        'settings': dict([(k, getattr(settings, k, None))
                          for k in whitelist])}


class CoverView(TemplateView):
    template_name = "main/cover.html"


class MapView(TemplateView):
    template_name = "main/map.html"


class SearchView(TemplateView):
    template_name = "main/search.html"


class PlaceDetailView(DetailView):
    model = Place


class PlaceUpdateView(LoggedInEditorMixin, ModelFormWidgetMixin, UpdateView):
    model = Place
    fields = ['title', 'notes']
    widgets = {
        'title': TextInput
    }


class LearningSiteDetailView(DetailView):
    model = LearningSite


class LearningSiteUpdateView(LoggedInEditorMixin, ModelFormWidgetMixin,
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


class DigitalObjectCreateView(LoggedInEditorMixin,
                              ModelFormWidgetMixin,
                              LearningSiteParamMixin,
                              CreateView):
    model = DigitalObject
    fields = ['file', 'description', 'datestamp', 'source_url']
    widgets = {
        'description': widgets.TextInput,
        'datestamp': widgets.SelectDateWidget()
    }

    def get_success_url(self):
        self.parent.digital_object.add(self.object)
        return reverse('site-gallery-view', args=[self.parent.id])


class DigitalObjectUpdateView(LoggedInEditorMixin,
                              ModelFormWidgetMixin,
                              LearningSiteRelatedMixin,
                              UpdateView):
    model = DigitalObject
    success_view = 'site-gallery-view'
    fields = ['file', 'description', 'datestamp', 'source_url']
    widgets = {
        'description': widgets.TextInput,
        'datestamp': widgets.SelectDateWidget()
    }


class DigitalObjectDeleteView(LoggedInEditorMixin,
                              LearningSiteRelatedMixin,
                              DeleteView):
    model = DigitalObject
    success_view = 'site-gallery-view'


class LearningSiteGalleryView(LearningSiteParamMixin, ListView):
    model = DigitalObject
    template_name = 'main/learningsite_gallery.html'

    def get_queryset(self):
        return self.parent.digital_object.all()


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
