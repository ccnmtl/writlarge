# pylint: disable-msg=R0904
from django.contrib import admin
from django.contrib.gis.db.models.fields import PointField
from django.contrib.gis.geos.point import Point
from django.forms.widgets import MultiWidget, TextInput
from django.urls.base import reverse
from django.utils.safestring import mark_safe

from writlarge.main.models import (
    LearningSite, ArchivalRepository, ArchivalCollection, DigitalObject,
    LearningSiteCategory, ArchivalRecordFormat, Place, ExtendedDate,
    Audience, InstructionalLevel, ArchivalCollectionSuggestion)


class LatLongWidget(MultiWidget):
    """
    A Widget that splits Point input into latitude/longitude text inputs.
    http://stackoverflow.com/a/33339847
    """

    def __init__(self, attrs=None, date_format=None, time_format=None):
        widgets = (TextInput(attrs=attrs), TextInput(attrs=attrs))
        super(LatLongWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return (value.coords[1], value.coords[0])
        return (None, None)

    def value_from_datadict(self, data, files, name):
        lat = data[name + '_0']
        lng = data[name + '_1']

        try:
            point = Point(float(lng), float(lat))
        except ValueError:
            return ''

        return point


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('title', 'latitude', 'longitude',
                    'created_at', 'modified_at')

    formfield_overrides = {
        PointField: {'widget': LatLongWidget},
    }


@admin.register(LearningSiteCategory)
class LearningSiteCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'group')


@admin.register(LearningSite)
class LearningSiteAdmin(admin.ModelAdmin):
    list_display = ('title', 'established', 'defunct',
                    'created_at', 'modified_at')


@admin.register(ArchivalRepository)
class ArchivalRepositoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'modified_at')


@admin.register(ArchivalCollection)
class ArchivalCollectionAdmin(admin.ModelAdmin):
    list_display = ('collection_title', 'description', 'repository',
                    'created_at', 'modified_at')


@admin.register(ArchivalCollectionSuggestion)
class ArchivalCollectionSuggestionAdmin(admin.ModelAdmin):
    list_display = (
        'repository_title', 'collection_title', 'archival_collection')
    exclude = ('record_format','archival_collection')
    actions = ['convert_suggested_collection']
    readonly_fields = ('inclusive_start', 'inclusive_end')

    def convert_suggested_collection(self, request, queryset):
        msgs = []
        created = '<a href="{}">{}</a> converted to archival collection. '
        exists = '<a href="{}">{}</a> archival collection already exists.'

        for obj in queryset:
            if obj.archival_collection:
                link = reverse('collection-detail-view',
                               kwargs={'pk': obj.archival_collection.id})
                msgs.append(exists.format(link, obj.collection_title))
            else:
                coll = obj.convert_to_archival_collection()
                link = reverse('collection-detail-view',
                               kwargs={'pk': coll.id})
                msgs.append(created.format(link, obj.collection_title))

        self.message_user(request, mark_safe('<br />'.join(msgs)))  # nosec

    convert_suggested_collection.short_description = \
        "Convert to ArchivalCollection"


admin.site.register(Audience)
admin.site.register(InstructionalLevel)
admin.site.register(DigitalObject)
admin.site.register(ArchivalRecordFormat)
admin.site.register(ExtendedDate)
