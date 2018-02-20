from django.test import TestCase
from writlarge.main.models import Place


class BasicModelTest(TestCase):
    def test_dummy(self):
        assert True


class PlaceTest(TestCase):

    def test_place(self):
        latlng = '50.06465,19.944979'
        pt = Place.objects.string_to_point(latlng)
        place = Place.objects.create(latlng=pt)

        self.assertEquals(place.__str__(), '')
        self.assertTrue(place.match_string(latlng))
        self.assertFalse(place.match_string('12.34,56.789'))
