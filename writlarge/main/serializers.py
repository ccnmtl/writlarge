from rest_framework import serializers

from django.contrib.gis.geos import Point
from writlarge.main.models import ArchivalRepository, LearningSite, \
    LearningSiteCategory, DigitalObject, Place


class StringListField(serializers.ListField):
    # from http://www.django-rest-framework.org/api-guide/fields/#listfield
    child = serializers.CharField()

    def to_representation(self, data):
        return ', '.join(data.values_list('name', flat=True))


class DigitalObjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DigitalObject
        fields = ('id', 'file', 'description', 'source_url')


class LearningSiteCategorySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = LearningSiteCategory
        fields = ('id', 'name', 'group')


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    latitude = serializers.SerializerMethodField(read_only=True)
    longitude = serializers.SerializerMethodField(read_only=True)

    def get_latitude(self, obj):
        return obj.latitude()

    def get_longitude(self, obj):
        return obj.longitude()

    def validate_latlng(self, data):
        if 'lat' in data and 'lng' in data:
            return Point(data['lng'], data['lat'])

    class Meta:
        model = Place
        fields = ('id', 'title', 'latlng', 'latitude', 'longitude',
                  'created_at', 'modified_at')


class ArchivalRepositorySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    place = PlaceSerializer()

    def create(self, validated_data):
        place_data = validated_data.pop('place')
        place = Place.objects.create(**place_data)
        repo = ArchivalRepository.objects.create(**validated_data)
        repo.place = place
        repo.save()
        return repo

    class Meta:
        model = ArchivalRepository
        fields = ('id', 'title', 'description', 'place', 'notes',
                  'created_at', 'modified_at')


class LearningSiteSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    category = LearningSiteCategorySerializer(read_only=True, many=True)
    digital_object = DigitalObjectSerializer(read_only=True, many=True)
    place = PlaceSerializer(many=True)
    tags = StringListField(read_only=True)
    family = serializers.SerializerMethodField(read_only=True)

    def get_family(self, obj):
        family = []
        for site in obj.descendants():
            family.append({
                'id': site.id,
                'title': site.title,
                'group': site.group(),
                'relationship': 'descendant'
            })
        for site in obj.antecedents():
            family.append({
                'id': site.id,
                'title': site.title,
                'group': site.group(),
                'relationship': 'antecedent'
            })
        for site in obj.associates():
            family.append({
                'id': site.id,
                'title': site.title,
                'group': site.group(),
                'relationship': 'associate'
            })
        return family

    class Meta:
        model = LearningSite
        fields = ('id', 'title', 'place', 'notes', 'category',
                  'digital_object', 'verified', 'verified_modified_at',
                  'empty', 'tags', 'created_at', 'modified_at',
                  'family')

    def create(self, validated_data):
        place_data = validated_data.pop('place')
        site = LearningSite.objects.create(**validated_data)

        for p in place_data:
            place = Place.objects.create(**p)
            site.place.add(place)
        return site

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        return instance
