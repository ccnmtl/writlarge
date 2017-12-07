from django.views.generic.base import TemplateView
from django.conf import settings


# returns important setting information for all web pages.
def django_settings(request):
    return {'settings':
            {'GOOGLE_MAP_API': getattr(settings, 'GOOGLE_MAP_API', '')}}


class IndexView(TemplateView):
    template_name = "main/index.html"
