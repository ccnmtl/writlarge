# pylint: disable-msg=R0904
from django.contrib import admin
from django.forms.widgets import MultiWidget, TextInput

from django.contrib.gis.db.models.fields import PointField
from django.contrib.gis.geos.point import Point
from writlarge.main.models import (
    LearningSite, ArchivalRepository, ArchivalCollection, DigitalObject,
    LearningSiteCategory, ArchivalRecordFormat, Place, ExtendedDate)


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
    list_display = ("title", "latitude", "longitude",
                    "created_at", "modified_at")

    formfield_overrides = {
        PointField: {'widget': LatLongWidget},
    }


@admin.register(LearningSite)
class LearningSiteAdmin(admin.ModelAdmin):
    list_display = ("title", "established", "defunct",
                    "created_at", "modified_at")

    formfield_overrides = {
        PointField: {'widget': LatLongWidget},
    }


@admin.register(ArchivalRepository)
class ArchivalRepositoryAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "modified_at")

    formfield_overrides = {
        PointField: {'widget': LatLongWidget},
    }


@admin.register(ArchivalCollection)
class ArchivalCollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "repository",
                    "created_at", "modified_at")


admin.site.register(DigitalObject)
admin.site.register(LearningSiteCategory)
admin.site.register(ArchivalRecordFormat)
admin.site.register(ExtendedDate)
