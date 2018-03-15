import random

from django.contrib.auth.models import User, Group, Permission
from django.contrib.gis.geos.point import Point
import factory
from factory.fuzzy import BaseFuzzyAttribute

from writlarge.main.models import (
    LearningSiteCategory, LearningSite, ExtendedDate,
    ArchivalRepository, Place, ArchivalCollection, Footnote)


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0),
                     random.uniform(-90.0, 90.0))


class ExtendedDateFactory(factory.DjangoModelFactory):
    class Meta:
        model = ExtendedDate
    edtf_format = '1984~'


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: "user%03d" % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')

    @factory.post_generation
    def group(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.groups.add(extracted)


class GroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = Group

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            lst = list(Permission.objects.filter(codename__in=extracted))
            self.permissions.add(*lst)


class LearningSiteCategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = LearningSiteCategory

    name = factory.Sequence(lambda n: "category%03d" % n)


class PlaceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Place

    latlng = FuzzyPoint()
    title = 'Cracow, Poland'


class LearningSiteFactory(factory.DjangoModelFactory):
    class Meta:
        model = LearningSite

    title = factory.Sequence(lambda n: "site%03d" % n)
    place = factory.SubFactory(PlaceFactory)
    established = factory.SubFactory(ExtendedDateFactory)
    defunct = factory.SubFactory(ExtendedDateFactory)
    created_by = factory.SubFactory(UserFactory)

    @factory.post_generation
    def category(self, create, extracted, **kwargs):
        if create:
            self.category.add(LearningSiteCategoryFactory())

    @factory.post_generation
    def place(self, create, extracted, **kwargs):
        if create:
            self.place.add(PlaceFactory())


class ArchivalRepositoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = ArchivalRepository

    title = factory.Sequence(lambda n: "repository%03d" % n)
    place = factory.SubFactory(PlaceFactory)


class ArchivalCollectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = ArchivalCollection

    title = factory.Sequence(lambda n: "collection%03d" % n)
    repository = factory.SubFactory(ArchivalRepositoryFactory)


class FootnoteFactory(factory.DjangoModelFactory):
    class Meta:
        model = Footnote

    note = factory.Sequence(lambda n: "footnote%03d" % n)
