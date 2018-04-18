from django.conf import settings
from django.contrib import messages
from django.db.models.query_utils import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls.base import reverse
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    UpdateView, CreateView, DeleteView, FormView)
from django.views.generic.list import ListView
from rest_framework import viewsets

from writlarge.main.forms import (
    ArchivalCollectionForm, ConnectionForm,
    ExtendedDateForm, LearningSiteForm, DigitalObjectForm, PlaceForm)
from writlarge.main.mixins import (
    LearningSiteParamMixin, LearningSiteRelatedMixin,
    LoggedInEditorMixin, JSONResponseMixin,
    SingleObjectCreatorMixin)
from writlarge.main.models import (
    LearningSite, LearningSiteRelationship, ArchivalRepository, Place,
    DigitalObject, ArchivalCollection, Footnote)
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


class SearchView(ListView):
    model = LearningSite
    template_name = "main/search.html"
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        query = self.request.GET.get('q', '')
        context['query'] = query

        base = reverse('search-view')
        context['base_url'] = u'{}?q={}&page='.format(base, query)

        return context

    def filter(self, qs):
        q = self.request.GET.get('q', '')
        if len(q) < 1:
            return qs

        return qs.filter(Q(title__icontains=q) |
                         Q(created_by__first_name__icontains=q) |
                         Q(created_by__last_name__icontains=q) |
                         Q(created_by__username__icontains=q))

    def get_queryset(self):
        qs = super(SearchView, self).get_queryset()
        qs = self.filter(qs)
        return qs


class PlaceCreateView(LoggedInEditorMixin,
                      LearningSiteParamMixin, CreateView):
    model = Place
    form_class = PlaceForm

    def get_success_url(self):
        self.parent.place.add(self.object)
        return reverse('site-detail-view', args=[self.parent.id])


class PlaceUpdateView(LoggedInEditorMixin,
                      LearningSiteRelatedMixin, UpdateView):
    model = Place
    form_class = PlaceForm
    success_view = 'site-detail-view'


class PlaceDeleteView(LoggedInEditorMixin,
                      LearningSiteRelatedMixin,
                      DeleteView):
    model = Place
    success_view = 'site-detail-view'


class LearningSiteDeleteView(LoggedInEditorMixin, SingleObjectCreatorMixin,
                             DeleteView):
    model = LearningSite

    def get_success_url(self):
        return reverse('map-view')


class LearningSiteDetailView(DetailView):
    model = LearningSite


class LearningSiteUpdateView(LoggedInEditorMixin, UpdateView):
    model = LearningSite
    form_class = LearningSiteForm


class DigitalObjectCreateView(LoggedInEditorMixin,
                              LearningSiteParamMixin,
                              CreateView):
    model = DigitalObject
    form_class = DigitalObjectForm

    def get_success_url(self):
        self.parent.digital_object.add(self.object)
        return reverse('site-gallery-view', args=[self.parent.id])


class DigitalObjectUpdateView(LoggedInEditorMixin,
                              LearningSiteRelatedMixin,
                              UpdateView):
    model = DigitalObject
    form_class = DigitalObjectForm
    success_view = 'site-gallery-view'


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


class ArchivalCollectionLinkView(LoggedInEditorMixin,
                                 LearningSiteParamMixin,
                                 TemplateView):
    template_name = 'main/archivalcollection_link.html'

    def get_context_data(self, *args, **kwargs):
        ctx = LearningSiteParamMixin.get_context_data(self, *args, **kwargs)
        ctx['collections'] = ArchivalCollection.objects.all()
        return ctx

    def post(self, *args, **kwargs):
        collection_id = self.request.POST.get('collection', None)
        collection = get_object_or_404(ArchivalCollection, pk=collection_id)
        collection.learning_sites.add(self.parent)

        messages.add_message(
            self.request, messages.INFO,
            '{} added as an archival resource.'.format(collection)
        )

        url = reverse('site-detail-view', args=[self.parent.id])
        return HttpResponseRedirect(url)


class ArchivalCollectionUnlinkView(LoggedInEditorMixin,
                                   TemplateView):
    template_name = 'main/archivalcollection_unlink.html'

    def get_parent(self):
        parent_id = self.kwargs.get('parent', None)
        return get_object_or_404(LearningSite, pk=parent_id)

    def get_collection(self):
        pk = self.kwargs.get('pk', None)
        return get_object_or_404(ArchivalCollection, pk=pk)

    def get_context_data(self, **kwargs):
        ctx = TemplateView.get_context_data(self, **kwargs)
        ctx['parent'] = self.get_parent()
        ctx['collection'] = self.get_collection()
        return ctx

    def post(self, *args, **kwargs):
        parent = self.get_parent()
        collection = self.get_collection()
        collection.learning_sites.remove(parent)

        messages.add_message(
            self.request, messages.INFO,
            '{} removed as an archival resource.'.format(collection)
        )

        url = reverse('site-detail-view', args=[parent.id])
        return HttpResponseRedirect(url)


class ArchivalCollectionCreateView(LoggedInEditorMixin,
                                   LearningSiteParamMixin,
                                   CreateView):
    model = ArchivalCollection
    form_class = ArchivalCollectionForm
    template_name = 'main/archivalcollection_create.html'

    def get_context_data(self, *args, **kwargs):
        ctx = LearningSiteParamMixin.get_context_data(self, *args, **kwargs)
        ctx['initial_repositories'] = ArchivalRepository.objects.all()
        return ctx

    def get_success_url(self):
        self.object.learning_sites.add(self.parent)

        messages.add_message(
            self.request, messages.INFO,
            '{} added as an archival resource.'.format(self.object.title)
        )
        return reverse('site-detail-view', args=[self.parent.id])


class ArchivalCollectionUpdateView(LoggedInEditorMixin,
                                   LearningSiteParamMixin,
                                   UpdateView):
    model = ArchivalCollection
    form_class = ArchivalCollectionForm

    def get_success_url(self):
        messages.add_message(
            self.request, messages.INFO,
            '{} has been updated.'.format(self.object.title)
        )
        return reverse('site-detail-view', args=[self.parent.id])


class ArchivalCollectionDeleteView(LoggedInEditorMixin,
                                   LearningSiteParamMixin,
                                   DeleteView):
    model = ArchivalCollection

    def get_success_url(self):
        messages.add_message(
            self.request, messages.INFO,
            '{} has been deleted.'.format(self.object.title)
        )
        return reverse('site-detail-view', args=[self.parent.id])


class FootnoteCreateView(LoggedInEditorMixin,
                         LearningSiteParamMixin,
                         CreateView):
    model = Footnote
    fields = ['ordinal', 'note']

    def get_success_url(self):
        self.parent.footnotes.add(self.object)
        return reverse('site-detail-view', args=[self.parent.id])


class FootnoteUpdateView(LoggedInEditorMixin,
                         LearningSiteRelatedMixin,
                         UpdateView):
    model = Footnote
    success_view = 'site-detail-view'
    fields = ['ordinal', 'note']


class FootnoteDeleteView(LoggedInEditorMixin,
                         LearningSiteRelatedMixin,
                         DeleteView):
    model = Footnote
    success_view = 'site-detail-view'


class DisplayDateView(JSONResponseMixin, View):

    def post(self, *args, **kwargs):
        form = ExtendedDateForm(self.request.POST)

        if not form.is_valid():
            return self.render_to_json_response({
                'success': False,
                'msg': form.get_error_messages()
            })
        else:
            return self.render_to_json_response({
                'success': True,
                'display': form.get_extended_date().__str__()
            })


class ConnectionCreateView(LoggedInEditorMixin,
                           LearningSiteParamMixin, FormView):

    template_name = 'main/connection.html'
    form_class = ConnectionForm

    def get_form(self, form_class=None):
        frm = FormView.get_form(self, form_class=form_class)

        ids = self.parent.connections()
        frm.fields['site'].queryset = \
            LearningSite.objects.exclude(id__in=ids)
        return frm

    def form_valid(self, form):
        if form.cleaned_data['connection_type'] == 'antecdent':
            form.cleaned_data['site'].children.add(self.parent)
        elif form.cleaned_data['connection_type'] == 'descendant':
            self.parent.children.add(form.cleaned_data['site'])
        elif form.cleaned_data['connection_type'] == 'associate':
            LearningSiteRelationship.objects.create(
                site_one=self.parent,
                site_two=form.cleaned_data['site'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('site-detail-view', args=[self.parent.id])


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
