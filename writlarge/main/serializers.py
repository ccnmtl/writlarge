from rest_framework import serializers

from writlarge.main.models import ArchivalRepository, LearningSite, \
    LearningSiteCategory, DigitalObject


class DigitalObjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DigitalObject
        fields = ('id', 'name', 'description', 'source_url')


class LearningSiteCategorySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = LearningSiteCategory
        fields = ('id', 'name')


class ArchivalRepositorySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ArchivalRepository
        fields = ('id', 'title', 'latlng', 'notes',
                  'verified', 'verified_modified_at',
                  'created_at', 'modified_at')


class LearningSiteSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    category = LearningSiteCategorySerializer(read_only=True, many=True)
    digital_object = DigitalObjectSerializer(read_only=True, many=True)

    class Meta:
        model = LearningSite
        fields = ('id', 'title', 'latlng', 'established', 'defunct', 'notes',
                  'category', 'digital_object',
                  'verified', 'verified_modified_at', 'created_at',
                  'modified_at')
