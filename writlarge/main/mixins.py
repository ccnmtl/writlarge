import collections
import json
import re

from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.forms.models import modelform_factory
from django.http.response import HttpResponseNotAllowed, HttpResponse, \
    HttpResponseRedirect
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape

from writlarge.main.models import LearningSite


def ajax_required(func):
    """
    AJAX request required decorator
    use it in your views:

    @ajax_required
    def my_view(request):
        ....

    """
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseNotAllowed("")
        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


class JSONResponseMixin(object):

    @method_decorator(ajax_required)
    def dispatch(self, *args, **kwargs):
        return super(JSONResponseMixin, self).dispatch(*args, **kwargs)

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(json.dumps(context),
                            content_type='application/json',
                            **response_kwargs)


class LearningSiteParamMixin(object):

    def dispatch(self, *args, **kwargs):
        try:
            parent_id = self.kwargs.get('parent', None)
            self.parent = LearningSite.objects.get(pk=parent_id)
        except LearningSite.DoesNotExist:
            self.parent = None

        return super(LearningSiteParamMixin, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(LearningSiteParamMixin, self).get_context_data(**kwargs)
        ctx['parent'] = self.parent
        return ctx


class LearningSiteRelatedMixin(object):

    def get_context_data(self, **kwargs):
        ctx = super(LearningSiteRelatedMixin, self).get_context_data(
            **kwargs)
        ctx['parent'] = self.object.learningsite_set.first()
        return ctx

    def get_success_url(self):
        parent_id = self.object.learningsite_set.first().id
        return reverse(self.success_view, args=[parent_id])


# https://stackoverflow.com/a/27971221/9322601
class ModelFormWidgetMixin(object):
    def get_form_class(self):
        return modelform_factory(self.model, fields=self.fields,
                                 widgets=self.widgets)


class LoggedInEditorMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):

        if (not self.request.user.groups or
                not self.request.user.groups.filter(name='Editor').exists()):
            return HttpResponseRedirect('/accounts/login/')

        return super(LoggedInEditorMixin, self).dispatch(*args, **kwargs)


class SingleObjectCreatorMixin(object):

    def dispatch(self, *args, **kwargs):
        if (not self.request.user == self.get_object().created_by and
                not self.request.user.is_staff):
            return HttpResponseRedirect('/accounts/login/')

        return super(
            SingleObjectCreatorMixin, self).dispatch(*args, **kwargs)


SearchToken = collections.namedtuple('Token', ['typ', 'value'])


class LearningSiteSearchMixin(object):

    def _tokenize(self, q):
        specification = [
            ('STRING',  r'"(.*?)"'),  # quoted string
            ('CATEGORY',  r'category:.*?($|\s)'),  # category
            ('TAG',  r'tag:.*?($|\s)'),  # tag
            ('SPACE', r'[ ]+'),
            ('CHARACTER', r'.'),  # Any other character
            ('END', r'$'),
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in specification)
        term = ''
        for mo in re.finditer(tok_regex, q):
            kind = mo.lastgroup
            value = mo.group(kind)
            if kind == 'CHARACTER':
                term += value
            elif (kind == 'SPACE' or kind == 'END') and len(term) > 0:
                yield SearchToken('STRING', term)
                term = ''
            elif kind == 'STRING':
                yield SearchToken(kind, value[1:-1])
            elif kind == 'CATEGORY':
                yield SearchToken(kind, value[9:].strip())
            elif kind == 'TAG':
                yield SearchToken(kind, value[4:].strip())

    def _process_query(self, qs, q):
        qs = qs.prefetch_related('category', 'tags')

        for token in self._tokenize(q):
            if token.typ == 'CATEGORY':
                qs = qs.filter(category__name=token.value)
            elif token.typ == 'TAG':
                qs = qs.filter(tags__name__in=[token.value])
            elif token.typ == 'STRING':
                qs = qs.filter(title__icontains=token.value)
        return qs

    def _process_years(self, qs, start, end):
        # exclude sites with invalid dates, and prefetch the foreign keys
        sites = qs.exclude(
            established__edtf_format='unknown',
            defunct__edtf_format='unknown').exclude(
                Q(established__isnull=True),
                Q(defunct__isnull=True)).prefetch_related(
                    'established', 'defunct')

        ids = []
        for site in sites:
            (min_year, max_year) = site.get_year_range()

            if min_year and (min_year > end):
                ids.append(site.id)
            elif max_year and (max_year < start):
                ids.append(site.id)

        return qs.exclude(id__in=ids)

    def filter(self, qs):
        # filter by a search term
        q = self.request.GET.get('q', None)
        if q:
            qs = self._process_query(qs, escape(q))

        # filter by start and end year
        start_year = self.request.GET.get('start', '')
        end_year = self.request.GET.get('end', '')
        if (re.match(r'[1-2][0-9]{3}', start_year) and
                re.match(r'[1-2][0-9]{3}', end_year)):
            qs = self._process_years(qs, int(start_year), int(end_year))

        return qs.select_related(
            'established', 'defunct',
            'created_by', 'modified_by').prefetch_related(
            'place', 'category', 'digital_object',
            'site_one', 'site_two', 'tags').order_by('title')
