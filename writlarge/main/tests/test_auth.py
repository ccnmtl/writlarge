from django.test import TestCase
from django.test.utils import override_settings

from writlarge.main.tests.factories import UserFactory, GroupFactory
from writlarge.main.auth import EditorMapper


@override_settings(WIND_STAFF_MAPPER_GROUPS=['foo.bar.local:columbia.edu'])
class TestWagtailEditorMapper(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.editor = GroupFactory(name='Editor')
        self.mapper = EditorMapper()

    def test_map_regular_user(self):
        self.assertEqual(self.user.groups.count(), 0)
        self.mapper.map(self.user, ['foo', 'bar', 'baz'])
        self.assertEqual(self.user.groups.count(), 0)

    def test_map_privileged_user(self):
        self.assertEqual(self.user.groups.count(), 0)
        self.mapper.map(self.user, ['foo', 'foo.bar.local:columbia.edu'])
        self.assertEqual(self.user.groups.count(), 1)
        self.assertEqual(self.user.groups.first(), self.editor)
