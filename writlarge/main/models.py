from django.contrib.auth.models import User
from django.contrib.gis.db.models.fields import PointField
from django.contrib.gis.geos.point import Point
from django.db import models
from django.urls.base import reverse
from taggit.managers import TaggableManager


class Footnote(models.Model):
    note = models.TextField()

    def __str__(self):
        return self.note


class DigitalObject(models.Model):
    file = models.FileField(upload_to="%Y/%m/%d/")
    description = models.TextField()

    datestamp = models.DateField(null=True, blank=True, verbose_name='Date')
    source_url = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Digital Object"
        ordering = ['-created_at']

    def __str__(self):
        return self.description


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

    description = models.TextField(null=True, blank=True)
    category = models.ManyToManyField(LearningSiteCategory, blank=True)
    digital_object = models.ManyToManyField(
        DigitalObject, blank=True)

    established = models.DateField(null=True, blank=True)
    defunct = models.DateField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    tags = TaggableManager(blank=True)

    instructional_level = models.TextField(null=True, blank=True)
    founder = models.TextField(null=True, blank=True)

    footnotes = models.ManyToManyField(Footnote, blank=True)

    verified = models.BooleanField(default=False)
    verified_modified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL,
        related_name='site_created_by')
    modified_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL,
        related_name='site_modified_by')

    class Meta:
        ordering = ['title']
        verbose_name = "Site of Teaching & Learning"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('site-detail-view', kwargs={'pk': self.id})

    def empty(self):
        return self.category.count() < 1


class ArchivalRepository(models.Model):
    title = models.TextField(unique=True, verbose_name="Repository Title")
    latlng = PointField()
    description = models.TextField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL,
        related_name='repository_created_by')
    modified_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL,
        related_name='repository_modified_by')

    class Meta:
        ordering = ['title']
        verbose_name = "Archival Repository"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'archival-repository-detail-view', kwargs={'pk': self.id})


class ArchivalCollection(models.Model):
    title = models.TextField(verbose_name="Collection Title")
    repository = models.ForeignKey(ArchivalRepository,
                                   on_delete=models.CASCADE)

    description = models.TextField(null=True, blank=True)
    learning_sites = models.ManyToManyField(LearningSite, blank=True)
    finding_aid_url = models.URLField(null=True, blank=True)
    linear_feet = models.FloatField(null=True, blank=True)
    record_format = models.ManyToManyField(ArchivalRecordFormat, blank=True)

    inclusive_start_date = models.DateField(null=True)
    inclusive_end_date = models.DateField(null=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL,
        related_name='collection_created_by')
    modified_by = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL,
        related_name='collection_modified_by')

    class Meta:
        ordering = ['title']
        verbose_name = "Archival Collection"

    def __str__(self):
        return self.title


class PlaceManager(models.Manager):

    def __init__(self, fields=None, *args, **kwargs):
        super(PlaceManager, self).__init__(
            *args, **kwargs)
        self._fields = fields

    @classmethod
    def string_to_point(cls, str):
        a = str.split(',')
        return Point(float(a[1].strip()), float(a[0].strip()))

    def get_or_create_from_string(self, latlng):
        point = self.string_to_point(latlng)

        created = False
        pl = Place.objects.filter(latlng=point).first()

        if pl is None:
            pl = Place.objects.create(latlng=point)
            created = True

        return pl, created


class Place(models.Model):
    objects = PlaceManager()

    title = models.TextField()
    latlng = PointField()

    digital_object = models.ManyToManyField(
        DigitalObject, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def latitude(self):
        return self.latlng.coords[1]

    def longitude(self):
        return self.latlng.coords[0]

    def match_string(self, latlng):
        s = '{},{}'.format(self.latitude(), self.longitude())
        return s == latlng

    def get_absolute_url(self):
        return reverse(
            'place-detail-view', kwargs={'pk': self.id})

    def empty(self):
        return True
