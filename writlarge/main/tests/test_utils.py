from django.test.testcases import TestCase
from writlarge.main.models import ExtendedDate
from writlarge.main.utils import (
    filter_fields, format_date_range, sanitize, validate_integer)


class TestUtils(TestCase):

    def test_filter_fields(self):
        data = {
            'established-millenium1': '1',
            'established-century1': '2',
            'defunct-millenium1': '3',
            'defunct-century1': '3',
        }
        data = filter_fields(data, 'established-')
        self.assertEqual(data['millenium1'], '1')
        self.assertEqual(data['century1'], '2')

    def test_format_date_range(self):
        unknown = ExtendedDate.objects.create(edtf_format='unknown')
        start = ExtendedDate.objects.create(edtf_format='2015')
        end = ExtendedDate.objects.create(edtf_format='2018')

        # has not ended
        self.assertEqual(
            format_date_range(None, False, None), '? - present')
        self.assertEqual(
            format_date_range(unknown, False, unknown), '? - present')
        self.assertEqual(
            format_date_range(start, False, None), '2015 - present')
        self.assertEqual(
            format_date_range(start, False, unknown), '2015 - present')
        self.assertEqual(
            format_date_range(start, False, end), '2015 - present')
        self.assertEqual(
            format_date_range(None, False, end), '? - present')

        # has ended
        self.assertEqual(
            format_date_range(None, True, None), '? - ?')
        self.assertEqual(
            format_date_range(unknown, True, unknown), '? - ?')
        self.assertEqual(
            format_date_range(start, True, None), '2015 - ?')
        self.assertEqual(
            format_date_range(start, True, unknown), '2015 - ?')
        self.assertEqual(
            format_date_range(start, True, end), '2015 - 2018')
        self.assertEqual(
            format_date_range(None, True, end), '? - 2018')
        self.assertEqual(
            format_date_range(unknown, True, end), '? - 2018')

    def test_sanitize(self):
        self.assertEqual(sanitize('s\0s'), '')
        self.assertEqual(sanitize('\x00s\x00s'), '')
        self.assertEqual(sanitize('s\0s\x00'), '')
        self.assertEqual(sanitize('query'), 'query')
        self.assertEqual(sanitize('<tag>'), '&lt;tag&gt;')
        self.assertEqual(sanitize(''), '')
        self.assertEqual(sanitize(None), '')

    def test_validate_integer(self):
        self.assertEqual(validate_integer('x71ksckz'), '')
        self.assertEqual(validate_integer(''), '')
        self.assertEqual(validate_integer(None), '')
        self.assertEqual(validate_integer('\x00'), '')
        self.assertEqual(validate_integer('1'), 1)
