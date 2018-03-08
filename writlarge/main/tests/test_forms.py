from django.test.testcases import TestCase

from writlarge.main.forms import (
    ExtendedDateForm, LearningSiteForm, DigitalObjectForm)
from writlarge.main.models import ExtendedDate
from writlarge.main.tests.factories import LearningSiteFactory


class ExtendedDateFormTest(TestCase):

    def test_clean_empty_fields(self):
        data = {
            'is_range': True,
            'millenium1': None, 'century1': '0', 'decade1': '1',
            'year1': '0', 'month1': '1', 'day1': '1',
            'approximate1': True, 'uncertain1': True,
            'millenium2': None, 'century2': '0', 'decade2': None,
            'year2': '1', 'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'Please specify a valid date<br />')

        data['millenium1'] = 2
        data['millenium2'] = 2
        ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'Please specify a valid date<br />')

    def test_clean_valid_date(self):
        data = {
            'is_range': False,
            'millenium1': '2', 'century1': '0', 'decade1': '1', 'year1': '0',
            'month1': '2', 'day1': '28',
            'approximate1': True, 'uncertain1': True,
            'millenium2': None, 'century2': None, 'decade2': None,
            'year2': None, 'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEquals(ExtendedDate.objects.count(), 0)

    def test_clean_valid_date_range(self):
        data = {
            'is_range': True,
            'millenium1': '2', 'century1': '0', 'decade1': '1', 'year1': '0',
            'month1': '2', 'day1': '28',
            'approximate1': True, 'uncertain1': True,
            'millenium2': '2', 'century2': '0', 'decade2': '1', 'year2': '2',
            'month2': '2', 'day2': '29',
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.get_error_messages(), '')
        self.assertEquals(ExtendedDate.objects.count(), 0)

        dt = form.save()
        self.assertEquals(ExtendedDate.objects.count(), 1)
        self.assertEquals(dt.edtf_format, '2010-02-28?~/2012-02-29')

    def test_clean_invalid_date(self):
        data = {
            'is_range': False,
            'millenium1': '2', 'century1': '2', 'decade1': '1',
            'year1': '0', 'month1': '2', 'day1': '31',
            'approximate1': True, 'uncertain1': True,
            'millenium2': None, 'century2': None, 'decade2': None,
            'year2': None, 'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'Please specify a valid date<br />')

        data['day1'] = 28
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'The date must be today or earlier<br />')

    def test_clean_invalid_date_ranges(self):
        data = {
            'is_range': True,
            'millenium1': '2', 'century1': '2', 'decade1': '1',
            'year1': '0', 'month1': '6', 'day1': '31',
            'approximate1': True, 'uncertain1': True,
            'millenium2': '2', 'century2': '2', 'decade2': '0',
            'year2': '9', 'month2': '9', 'day2': '31',
            'approximate2': False, 'uncertain2': False,
        }

        # invalid start date
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'Please specify a valid date<br />')
        self.assertEquals(ExtendedDate.objects.count(), 0)

        # invalid end date
        data['day1'] = '30'
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.get_error_messages(),
            u'Please specify a valid date<br />')
        self.assertEquals(ExtendedDate.objects.count(), 0)

        # start year in the future
        data['day2'] = 30
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'All dates must be today or earlier<br />')
        self.assertEquals(ExtendedDate.objects.count(), 0)

        # end year in the future
        data['century1'] = 0
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'All dates must be today or earlier<br />')
        self.assertEquals(ExtendedDate.objects.count(), 0)

        # start > end
        data['century2'] = 0
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.get_error_messages(),
            u'The start date must be earlier than the end date.<br />')
        self.assertEquals(ExtendedDate.objects.count(), 0)

    def test_clean_incomplete_data(self):
        data = {
            'approximate1': True, 'approximate2': False,
            'century1': None, 'century2': None, 'day1': None, 'day2': None,
            'decade1': None, 'decade2': None, 'is_range': False,
            'millenium1': 1, 'millenium2': None,
            'month1': None, 'month2': None,
            'uncertain1': True, 'uncertain2': False,
            'year1': None, 'year2': None
        }
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())

        self.assertEquals(form.get_error_messages(),
                          u'Please specify a valid date<br />')

    def test_create_or_update(self):
        site = LearningSiteFactory(established=None)

        data = {
            'is_range': False,
            'millenium1': '2', 'century1': '0', 'decade1': '1', 'year1': '0',
            'month1': '2', 'day1': '28',
            'approximate1': True, 'uncertain1': True,
            'millenium2': None, 'century2': None, 'decade2': None,
            'year2': None, 'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False,
        }

        # add established date
        form = ExtendedDateForm(data=data)
        self.assertTrue(form.is_valid())
        form.create_or_update(site, 'established')
        site.refresh_from_db()
        established = site.established
        self.assertEquals(established.edtf_format, '2010-02-28?~')

        # update established date
        data['year1'] = 1
        form = ExtendedDateForm(data=data)
        self.assertTrue(form.is_valid())
        form.create_or_update(site, 'established')
        site.refresh_from_db()
        self.assertEquals(established.id, site.established.id)
        self.assertEquals(established.edtf_format, '2011-02-28?~')

        # remove established date
        data = {
            'is_range': False,
            'millenium1': '', 'century1': '', 'decade1': '', 'year1': '',
            'month1': '', 'day1': '',
            'approximate1': True, 'uncertain1': True,
            'millenium2': '', 'century2': '', 'decade2': '',
            'year2': '', 'month2': '', 'day2': '',
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertTrue(form.is_valid())
        form.create_or_update(site, 'established')
        site.refresh_from_db()
        self.assertIsNone(site.established)

        with self.assertRaises(ExtendedDate.DoesNotExist):
            ExtendedDate.objects.get(id=established.id)


class LearningSiteFormTest(TestCase):

    def test_clean_fields(self):
        data = {
            'established-is_range': False,
            'established-millenium1': '2', 'established-century1': '0',
            'established-decade1': '1', 'established-year1': '0',
            'established-month1': '', 'established-day1': '',
            'established-approximate1': True, 'established-uncertain1': True,
            'defunct-is_range': False,
            'defunct-millenium1': '3', 'defunct-century1': '0',
            'defunct-decade1': '1', 'defunct-year1': '0',
            'defunct-month1': '', 'defunct-day1': '',
            'defunct-approximate1': True, 'defunct-uncertain1': True,
        }
        form = LearningSiteForm(data=data)
        self.assertFalse(form.is_valid())

        self.assertTrue('defunct' in form.errors)
        self.assertFalse('established' in form.errors)

        self.assertTrue(
            'Please specify a valid date' in form.errors['defunct'])
        self.assertTrue(
            'millenium1' in form.errors['defunct'])

    def test_save(self):
        site = LearningSiteFactory(defunct=None)
        data = {
            'title': 'Foo',
            'latlng': site.latlng,
            'established-is_range': False,
            'established-millenium1': '2', 'established-century1': '0',
            'established-decade1': '0', 'established-year1': '8',
            'established-month1': '', 'established-day1': '',
            'established-approximate1': True, 'established-uncertain1': True,
            'defunct-is_range': False,
            'defunct-millenium1': '2', 'defunct-century1': '0',
            'defunct-decade1': '1', 'defunct-year1': '1',
            'defunct-month1': '', 'defunct-day1': '',
            'defunct-approximate1': False, 'defunct-uncertain1': False,
        }
        form = LearningSiteForm(data, instance=site)
        self.assertTrue(form.is_valid())
        form.save()

        # make sure this was all saved
        self.assertEquals(site.established.edtf_format, '2008?~')
        self.assertEquals(site.defunct.edtf_format, '2011')


class TestDigitalObjectForm(TestCase):

    def test_form_clean_errors(self):
        form = DigitalObjectForm()
        form._errors = {}
        form.cleaned_data = {
            'file': '',
            'source_url': '',
        }

        form.clean()
        self.assertEquals(len(form.errors), 3)
        self.assertTrue('file' in form.errors)
        self.assertTrue('source_url' in form.errors)
        self.assertTrue('__all__' in form.errors)

    def test_form_clean_success(self):
        form = DigitalObjectForm()
        form._errors = {}
        form.cleaned_data = {
            'file': '',
            'source_url': 'https://writlarge.ctl.columbia.edu',
        }

        form.clean()
        self.assertEquals(len(form.errors), 0)
