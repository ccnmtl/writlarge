from django.contrib.gis.db.models.fields import PointField
from django.db import models
from django.urls.base import reverse
from taggit.managers import TaggableManager


class DigitalObject(models.Model):
    name = models.TextField()
    file = models.FileField(upload_to="%Y/%m/%d/")
    description = models.TextField()

    source_url = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Digital Object"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class LearningSiteCategory(models.Model):
    name = models.TextField(unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ArchivalRecordFormat(models.Model):
    name = models.TextField(unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LearningSite(models.Model):
    title = models.TextField(unique=True)
    latlng = PointField()

    category = models.ManyToManyField(LearningSiteCategory, blank=True)
    digital_object = models.ManyToManyField(
        DigitalObject, blank=True)

    established = models.DateField(null=True, blank=True)
    defunct = models.DateField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    tags = TaggableManager(blank=True)

    verified = models.BooleanField(default=False)
    verified_modified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = "Site of Teaching & Learning"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('learning-site-detail-view', kwargs={'pk': self.id})


class ArchivalRepository(models.Model):
    title = models.TextField(unique=True)
    latlng = PointField(null=True)
    notes = models.TextField(null=True, blank=True)
    tags = TaggableManager()

    verified = models.BooleanField(default=False)
    verified_modified_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = "Archival Repository"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'archival-repository-detail-view', kwargs={'pk': self.id})


class ArchivalCollection(models.Model):
    title = models.TextField()
    description = models.TextField()
    learning_sites = models.ManyToManyField(LearningSite)
    repository = models.ForeignKey(ArchivalRepository,
                                   on_delete=models.CASCADE)

    finding_aid_url = models.URLField()
    linear_feet = models.FloatField()
    record_format = models.ManyToManyField(ArchivalRecordFormat)

    inclusive_start_date = models.DateField(null=True)
    inclusive_end_date = models.DateField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = "Archival Collection"

    def __str__(self):
        return self.title
