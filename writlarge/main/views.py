from django.conf import settings
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from writlarge.main.models import LearningSite, ArchivalRepository


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
