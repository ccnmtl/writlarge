from django.test import TestCase

from writlarge.main.models import Place, ExtendedDate, LearningSite
from writlarge.main.tests.factories import (
    ExtendedDateFactory, LearningSiteFactory,
    LearningSiteRelationshipFactory)


class ExtendedDateTest(TestCase):

    use_cases = {
        '999': 'invalid',
        '1uuu': '2nd millenium',
        '2uuu': '3rd millenium',
        '14uu': '1400s',  # PRECISION_CENTURY
        '192u': '1920s',  # PRECISION_DECADE
        '1613': '1613',  # PRECISION_YEAR
        '1944-11': 'November 1944',  # PRECISION_MONTH
        '1659-06-30': 'June 30, 1659',  # PRECISION_DAY
        '1659~': 'c. 1659',  # uncertain
        '1659?': '1659?',  # approximate
        '1659?~': 'c. 1659?',  # approximate & uncertain
        '16uu/1871': '1600s - 1871',
        '1557-09/1952-01-31': 'September 1557 - January 31, 1952',
        '1829/open': '1829 - present',
        'unknown/1736': '? - 1736',
    }

    def test_use_cases(self):
        for key, val in self.use_cases.items():
            e = ExtendedDate(edtf_format=key)
            self.assertEquals(e.__str__(), val)

    def test_create_from_dict_empty(self):
        values = {
            'is_range': False,
            'millenium1': None, 'century1': None, 'decade1': None,
            'year1': None, 'month1': None, 'day1': None,
            'approximate1': False, 'uncertain1': False}

        dt = ExtendedDate.objects.from_dict(values)
        self.assertEquals(dt.edtf_format, 'unknown')
        self.assertEquals(dt.__str__(), '?')

    def test_create_from_dict(self):
        values = {
            'is_range': True,
            'millenium1': 2, 'century1': 0, 'decade1': 0, 'year1': 1,
            'month1': 1, 'day1': 1,
            'approximate1': True, 'uncertain1': True,
            'millenium2': 2, 'century2': 0, 'decade2': None, 'year2': None,
            'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False}

        dt = ExtendedDate.objects.from_dict(values)
        self.assertEquals(dt.edtf_format, '2001-01-01?~/20uu')

    def test_create_from_dict_missing_elements(self):
        values = {
            'is_range': True,
            'millenium1': 2, 'century1': 0, 'decade1': 0, 'year1': 1,
            'month1': 1,
            'approximate1': True, 'uncertain1': True,
            'millenium2': 2, 'century2': 0, 'decade2': None, 'year2': None,
            'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False}

        dt = ExtendedDate.objects.from_dict(values)
        self.assertEquals(dt.edtf_format, '2001-01?~/20uu')

    def test_to_edtf(self):
        mgr = ExtendedDate.objects
        dt = mgr.to_edtf(2, None, None, None, None, None, True, True)
        self.assertEquals(dt, '2uuu?~')

        dt = mgr.to_edtf(2, 0, None, None, None, None, True, True)
        self.assertEquals(dt, '20uu?~')

        dt = mgr.to_edtf(2, 0, 1, 5, None, None, False, False)
        self.assertEquals(dt, '2015')

        dt = mgr.to_edtf(2, 0, 1, 5, 2, None, False, False)
        self.assertEquals(dt, '2015-02')

        dt = mgr.to_edtf(2, 0, 1, 5, 12, 31, False, False)
        self.assertEquals(dt, '2015-12-31')

    def test_match_string(self):
        edtf = ExtendedDateFactory()
        self.assertTrue(edtf.match_string('approximately 1984'))
        self.assertFalse(edtf.match_string('1984'))

    def test_create_from_string(self):
        dt = ExtendedDate.objects.create_from_string('approximately 1983')
        self.assertEquals(dt.edtf_format, '1983~')

        dt = ExtendedDate.objects.create_from_string('before 1984')
        self.assertEquals(dt.edtf_format, 'unknown/1984')

    def test_invalid_month(self):
        dt = ExtendedDate.objects.create(edtf_format='1980-uu-17/1997-uu-18')
        self.assertEquals(dt.__str__(),
                          'unknown month 17, 1980 - unknown month 18, 1997')

    def test_to_dict_invalid(self):
        dt = ExtendedDate.objects.create(edtf_format='999')
        d = dt.to_dict()
        self.assertEquals(len(d), 0)

    def test_to_dict_partial(self):
        dt = ExtendedDate.objects.create(edtf_format='1uuu')
        d = dt.to_dict()
        self.assertFalse(d['approximate1'])
        self.assertFalse(d['uncertain1'])
        self.assertEquals(d['millenium1'], '1')
        self.assertIsNone(d['century1'])
        self.assertIsNone(d['decade1'])
        self.assertIsNone(d['year1'])
        self.assertIsNone(d['month1'])
        self.assertIsNone(d['day1'])

    def test_to_dict_full(self):
        dt = ExtendedDate.objects.create(edtf_format='1659-06-30?~')
        d = dt.to_dict()
        self.assertTrue(d['approximate1'])
        self.assertTrue(d['uncertain1'])
        self.assertEquals(d['millenium1'], '1')
        self.assertEquals(d['century1'], '6')
        self.assertEquals(d['decade1'], '5')
        self.assertEquals(d['year1'], '9')
        self.assertEquals(d['month1'], '06')
        self.assertEquals(d['day1'], '30')


class PlaceTest(TestCase):

    def test_place(self):
        latlng = '50.06465,19.944979'
        pt = Place.objects.string_to_point(latlng)
        place = Place.objects.create(latlng=pt)

        self.assertEquals(place.__str__(), '')
        self.assertTrue(place.match_string(latlng))
        self.assertFalse(place.match_string('12.34,56.789'))


class LearningSiteTest(TestCase):

    def test_parent_child_relationships(self):
        parent = LearningSiteFactory()
        child = LearningSiteFactory()

        parent.children.add(child)

        self.assertTrue(parent.has_connections())
        self.assertTrue(child.has_connections())

        lst = child.antecedents()
        self.assertEquals(len(lst), 1)
        self.assertEquals(lst[0], parent)

        lst = parent.descendants()
        self.assertEquals(len(lst), 1)
        self.assertEquals(lst[0], child)

    def test_empty_relationships(self):
        site = LearningSiteFactory()
        self.assertFalse(site.has_connections())

    def test_relationships(self):
        r = LearningSiteRelationshipFactory()
        self.assertTrue(r.site_one.has_connections())
        self.assertTrue(r.site_two.has_connections())

        qs = r.site_one.associates()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs[0], r.site_two)

        qs = r.site_two.associates()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs[0], r.site_one)

    def test_empty(self):
        site = LearningSiteFactory()
        self.assertFalse(site.empty())

        site = LearningSite.objects.create(title='Foo')
        self.assertTrue(site.empty())

    def test_connections(self):
        parent = LearningSiteFactory()
        child = LearningSiteFactory()
        sib = LearningSiteFactory()
        sib2 = LearningSiteFactory()

        parent.children.add(child)
        LearningSiteRelationshipFactory(site_one=parent, site_two=sib)
        LearningSiteRelationshipFactory(site_one=sib2, site_two=parent)

        ids = parent.connections()
        self.assertEquals(len(ids), 4)

        self.assertTrue(parent.id in ids)
        self.assertTrue(child.id in ids)
        self.assertTrue(sib.id in ids)
        self.assertTrue(sib2.id in ids)

        ids = child.connections()
        self.assertEquals(len(ids), 2)
        self.assertTrue(child.id in ids)
        self.assertTrue(parent.id in ids)

    def test_group(self):
        site = LearningSite.objects.create(title='test site')
        self.assertEquals(site.group(), 'other')

        site = LearningSiteFactory()
        self.assertEquals(site.group(), 'school')
