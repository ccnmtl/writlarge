import datetime
import random

from IPython.utils.tz import UTC
from django.contrib.auth.models import User, Group, Permission
from django.contrib.gis.geos.point import Point
import factory
from factory.fuzzy import BaseFuzzyAttribute, FuzzyDateTime

from writlarge.main.models import LearningSiteCategory, LearningSite, \
    ArchivalRepository


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0),
                     random.uniform(-90.0, 90.0))


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


class LearningSiteFactory(factory.DjangoModelFactory):
    class Meta:
        model = LearningSite

    title = factory.Sequence(lambda n: "site%03d" % n)
    latlng = FuzzyPoint()
    established = FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=UTC))
    defunct = FuzzyDateTime(datetime.datetime(2009, 1, 1, tzinfo=UTC))

    @factory.post_generation
    def category(self, create, extracted, **kwargs):
        if create:
            self.category.add(LearningSiteCategoryFactory())


class ArchivalRepositoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = ArchivalRepository

    title = factory.Sequence(lambda n: "repository%03d" % n)
    latlng = FuzzyPoint()
