from django.test.testcases import TestCase

from writlarge.main.utils import filter_fields


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
