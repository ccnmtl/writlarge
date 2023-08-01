import random

from django.contrib.auth.models import User, Group, Permission
from django.contrib.gis.geos.point import Point
import factory
from factory.fuzzy import BaseFuzzyAttribute

from writlarge.main.models import (
    LearningSiteCategory, LearningSite, LearningSiteRelationship,
    ExtendedDate, ArchivalRepository, Place, ArchivalCollection, Footnote,
    ArchivalCollectionSuggestion)


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0),
                     random.uniform(-90.0, 90.0))


class ExtendedDateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExtendedDate
    edtf_format = '1984~'


class UserFactory(factory.django.DjangoModelFactory):
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


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            lst = list(Permission.objects.filter(codename__in=extracted))
            self.permissions.add(*lst)


class LearningSiteCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LearningSiteCategory

    name = factory.Sequence(lambda n: "category%03d" % n)
    group = 'school'


class PlaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Place

    latlng = FuzzyPoint()
    title = 'Cracow, Poland'
    start_date = factory.SubFactory(ExtendedDateFactory)
    end_date = factory.SubFactory(ExtendedDateFactory)


class LearningSiteFactory(factory.django.DjangoModelFactory):
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
    def place(self, create, extracted, **kwargs): # noqa F811
        if create:
            self.place.add(PlaceFactory())


class ArchivalRepositoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ArchivalRepository

    title = factory.Sequence(lambda n: "repository%03d" % n)
    place = factory.SubFactory(PlaceFactory)


class ArchivalCollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ArchivalCollection

    collection_title = factory.Sequence(lambda n: "collection%03d" % n)
    repository = factory.SubFactory(ArchivalRepositoryFactory)


class ArchivalCollectionSuggestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ArchivalCollectionSuggestion

    repository_title = factory.Sequence(lambda n: "repository%03d" % n)
    collection_title = factory.Sequence(lambda n: "collection%03d" % n)

    person = 'Elizabeth B. Drewry'
    person_title = 'Director of the Roosevelt Library'
    email = 'edrewry@rooseveltlibrary.org'

    latlng = FuzzyPoint()
    title = 'Hyde Park, NY'

    description = 'Sample description'
    finding_aid_url = 'https://fdrlibrary.org/finding-aids'
    linear_feet = 3

    inclusive_start = factory.SubFactory(ExtendedDateFactory)
    inclusive_end = factory.SubFactory(ExtendedDateFactory)


class FootnoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Footnote

    note = factory.Sequence(lambda n: "footnote%03d" % n)


class LearningSiteRelationshipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LearningSiteRelationship

    site_one = factory.SubFactory(LearningSiteFactory)
    site_two = factory.SubFactory(LearningSiteFactory)
