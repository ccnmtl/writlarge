# pylint: disable-msg=R0904
from django.contrib import admin

from writlarge.main.models import LearningSite, ArchivalRepository, \
    ArchivalCollection, DigitalObject, LearningSiteCategory, \
    ArchivalRecordFormat


@admin.register(LearningSite)
class LearningSiteAdmin(admin.ModelAdmin):
    list_display = ("title", "established", "defunct",
                    "created_at", "modified_at")


@admin.register(ArchivalRepository)
class ArchivalRepositoryAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "modified_at")


@admin.register(ArchivalCollection)
class ArchivalCollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "repository",
                    "created_at", "modified_at")


admin.site.register(DigitalObject)
admin.site.register(LearningSiteCategory)
admin.site.register(ArchivalRecordFormat)
