import datetime

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models.query_utils import Q
from django.http import Http404
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
    ArchivalCollectionCreateForm, ArchivalCollectionUpdateForm,
    ArchivalCollectionSuggestionForm, ConnectionForm,
    ExtendedDateForm, LearningSiteForm, DigitalObjectForm, PlaceForm)
from writlarge.main.mixins import (
    LearningSiteParamMixin, LearningSiteRelatedMixin,
    LoggedInEditorMixin, JSONResponseMixin, LearningSiteSearchMixin,
    SingleObjectCreatorMixin)
from writlarge.main.models import (
    LearningSite, LearningSiteRelationship, ArchivalRepository, Place,
    DigitalObject, ArchivalCollection, Footnote,
    ArchivalCollectionSuggestion)
from writlarge.main.serializers import (
    ArchivalRepositorySerializer, LearningSiteSerializer, PlaceSerializer,
    LearningSiteFamilySerializer)
from writlarge.main.utils import sanitize, validate_integer


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

    def get_min_year(self, qs):
        site = min(
            qs, key=lambda site: site.get_year_range()[0] or float('inf'))
        return site.get_year_range()[0]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MapView, self).get_context_data(**kwargs)

        qs = LearningSite.objects.all().select_related(
            'established', 'defunct')

        context['min_year'] = self.get_min_year(qs)
        context['max_year'] = datetime.date.today().year
        return context


class SearchView(LearningSiteSearchMixin, ListView):
    model = LearningSite
    template_name = "main/search.html"
    paginate_by = 15

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        query = self.request.GET.get('q', '')
        context['query'] = query

        base = reverse('search-view')
        context['base_url'] = u'{}?q={}&page='.format(base, query)

        return context

    def get_queryset(self):
        qs = super(SearchView, self).get_queryset()
        return self.filter(qs, True)


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
        if not self.parent:
            raise Http404('')

        return self.parent.digital_object.all()


class ArchivalCollectionDetailView(DetailView):
    model = ArchivalCollection


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
    form_class = ArchivalCollectionCreateForm
    template_name = 'main/archivalcollection_create.html'

    def get_context_data(self, *args, **kwargs):
        ctx = LearningSiteParamMixin.get_context_data(self, *args, **kwargs)
        ctx['initial_repositories'] = ArchivalRepository.objects.all()
        return ctx

    def get_success_url(self):
        self.object.learning_sites.add(self.parent)

        messages.add_message(
            self.request, messages.INFO,
            '{} added as an archival resource.'.format(
                self.object.collection_title)
        )
        return reverse('site-detail-view', args=[self.parent.id])


class ArchivalCollectionSuggestView(CreateView):
    model = ArchivalCollectionSuggestion
    form_class = ArchivalCollectionSuggestionForm
    template_name = 'main/archivalcollection_suggest.html'
    success_url = ''

    def get_form_kwargs(self):
        kw = super(ArchivalCollectionSuggestView, self).get_form_kwargs()
        kw['request'] = self.request
        return kw

    def get_context_data(self, *args, **kwargs):
        ctx = CreateView.get_context_data(self, *args, **kwargs)
        ctx['initial_repositories'] = ArchivalRepository.objects.all()
        return ctx

    def get_success_url(self):
        return reverse('collection-suggest-success-view')

    def form_valid(self, form):
        result = CreateView.form_valid(self, form)

        url = 'https://{}/admin/main/archivalcollectionsuggestion/{}/'.format(
            self.request.get_host(), form.instance.id)
        msg = '''
            An archival collection was suggested. See details here: {}
        '''.format(url)

        # Send an email to the team
        send_mail('Archival Collection Suggested',
                  msg, settings.SERVER_EMAIL, (settings.CONTACT_US_EMAIL,))

        return result


class ArchivalCollectionSuggestSuccessView(TemplateView):
    template_name = 'main/archivalcollection_suggest_success.html'


class ArchivalCollectionUpdateView(LoggedInEditorMixin,
                                   LearningSiteParamMixin,
                                   UpdateView):
    model = ArchivalCollection
    form_class = ArchivalCollectionUpdateForm

    def get_success_url(self):
        messages.add_message(
            self.request, messages.INFO,
            '{} has been updated.'.format(self.object.collection_title)
        )
        if self.parent:
            return reverse('site-detail-view', args=[self.parent.id])
        else:
            return reverse('collection-detail-view',
                           args=[self.object.id])


class ArchivalCollectionDeleteView(LoggedInEditorMixin,
                                   LearningSiteParamMixin,
                                   DeleteView):
    model = ArchivalCollection

    def get_success_url(self):
        messages.add_message(
            self.request, messages.INFO,
            '{} has been deleted.'.format(self.object.collection_title)
        )
        return reverse('site-detail-view', args=[self.parent.id])


class ArchivalCollectionListView(ListView):

    model = ArchivalCollection
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(
            ArchivalCollectionListView, self).get_context_data(**kwargs)

        query = self.request.GET.get('q', '')
        context['query'] = query

        repo = self.request.GET.get('rid', '')
        repo = validate_integer(repo)
        if repo:
            try:
                context['selected_repository'] = \
                    ArchivalRepository.objects.get(id=repo)
            except ArchivalRepository.DoesNotExist:
                pass

        base = reverse('archival-collections')
        context['base_url'] = \
            u'{}?q={}&rid={}&page='.format(base, query, repo)

        ids = self.get_queryset().values_list('id', flat=True)
        context['repositories'] = ArchivalRepository.objects.filter(
            archivalcollection__id__in=ids).distinct()

        return context

    def filter(self, qs):
        q = self.request.GET.get('q', '')
        q = sanitize(q)
        if len(q) > 0:
            qs = qs.filter(Q(collection_title__icontains=q) |
                           Q(repository__title__icontains=q))

        repo = self.request.GET.get('rid', '')
        repo = validate_integer(repo)
        if repo:
            qs = qs.filter(repository__id=repo)

        return qs

    def get_queryset(self):
        qs = super(ArchivalCollectionListView, self).get_queryset()
        qs = self.filter(qs)
        return qs


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
        ids.append(self.parent.id)
        frm.fields['site'].queryset = \
            LearningSite.objects.exclude(id__in=ids)
        return frm

    def form_valid(self, form):
        LearningSiteRelationship.objects.create(
            site_one=self.parent,
            site_two=form.cleaned_data['site'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('site-detail-view', args=[self.parent.id])


class ConnectionDeleteView(LoggedInEditorMixin, LearningSiteParamMixin,
                           DeleteView):

    model = LearningSite
    template_name = 'main/connection_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        success_url = reverse('site-detail-view', args=[self.parent.id])

        site = self.get_object()

        lsr = LearningSiteRelationship.objects.filter(
            Q(site_one=self.parent, site_two=site) |
            Q(site_one=site, site_two=self.parent))
        lsr.delete()

        return HttpResponseRedirect(success_url)


"""
Rest API endpoints
"""


class ArchivalRepositoryViewSet(viewsets.ModelViewSet):
    queryset = ArchivalRepository.objects.all().order_by('-modified_at')
    serializer_class = ArchivalRepositorySerializer


class LearningSiteViewSet(LearningSiteSearchMixin, viewsets.ModelViewSet):
    serializer_class = LearningSiteSerializer

    def get_queryset(self):
        qs = LearningSite.objects.all()
        return self.filter(qs)


class LearningSiteFamilyViewSet(viewsets.ModelViewSet):
    queryset = LearningSite.objects.all()
    serializer_class = LearningSiteFamilySerializer


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all().order_by('-modified_at')
    serializer_class = PlaceSerializer
