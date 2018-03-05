from django.test.testcases import TestCase

from writlarge.main.forms import ExtendedDateForm
from writlarge.main.models import ExtendedDate


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
