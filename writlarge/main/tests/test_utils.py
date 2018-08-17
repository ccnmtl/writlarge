from django.test.testcases import TestCase

from writlarge.main.models import ExtendedDate
from writlarge.main.utils import filter_fields, format_date_range


class TestUtils(TestCase):

    def test_filter_fields(self):
        data = {
            'established-millenium1': '1',
            'established-century1': '2',
            'defunct-millenium1': '3',
            'defunct-century1': '3',
        }
        data = filter_fields(data, 'established-')
        self.assertEquals(data['millenium1'], '1')
        self.assertEquals(data['century1'], '2')

    def test_format_date_range(self):
        unknown = ExtendedDate.objects.create(edtf_format='unknown')
        start = ExtendedDate.objects.create(edtf_format='2015')
        end = ExtendedDate.objects.create(edtf_format='2018')

        # has not ended
        self.assertEquals(
            format_date_range(None, False, None), '? - present')
        self.assertEquals(
            format_date_range(unknown, False, unknown), '? - present')
        self.assertEquals(
            format_date_range(start, False, None), '2015 - present')
        self.assertEquals(
            format_date_range(start, False, unknown), '2015 - present')
        self.assertEquals(
            format_date_range(start, False, end), '2015 - present')
        self.assertEquals(
            format_date_range(None, False, end), '? - present')

        # has ended
        self.assertEquals(
            format_date_range(None, True, None), '? - ?')
        self.assertEquals(
            format_date_range(unknown, True, unknown), '? - ?')
        self.assertEquals(
            format_date_range(start, True, None), '2015 - ?')
        self.assertEquals(
            format_date_range(start, True, unknown), '2015 - ?')
        self.assertEquals(
            format_date_range(start, True, end), '2015 - 2018')
        self.assertEquals(
            format_date_range(None, True, end), '? - 2018')
        self.assertEquals(
            format_date_range(unknown, True, end), '? - 2018')
