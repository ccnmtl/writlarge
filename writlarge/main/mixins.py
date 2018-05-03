import json

from django.contrib.auth.decorators import login_required
from django.forms.models import modelform_factory
from django.http.response import HttpResponseNotAllowed, HttpResponse, \
    HttpResponseRedirect
from django.urls.base import reverse
from django.utils.decorators import method_decorator

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
                not self.request.user.is_superuser):
            return HttpResponseRedirect('/accounts/login/')

        return super(
            SingleObjectCreatorMixin, self).dispatch(*args, **kwargs)
