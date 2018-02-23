from json import loads, dumps

from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.test.utils import override_settings
from django.urls.base import reverse

from writlarge.main.tests.factories import (
    UserFactory, LearningSiteFactory, ArchivalRepositoryFactory, GroupFactory)
from writlarge.main.views import django_settings, DigitalObjectCreateView


class BasicTest(TestCase):
    def setUp(self):
        self.c = Client()

    def test_root(self):
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)

    def test_smoketest(self):
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'PASS')

    @override_settings(GOOGLE_MAP_API=['123456'])
    def test_django_settings(self):
        request = RequestFactory()
        request.user = UserFactory()

        ctx = django_settings(request)
        self.assertEquals(ctx['settings']['GOOGLE_MAP_API'], ['123456'])
        self.assertFalse(ctx['is_editor'])

        request.user.groups.add(GroupFactory(name='Editor'))
        ctx = django_settings(request)
        self.assertTrue(ctx['is_editor'])


class PasswordTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = UserFactory()

    def test_logged_out(self):
        response = self.client.get('/accounts/password_change/')
        self.assertEquals(response.status_code, 302)

        response = self.client.get('/accounts/password_reset/')
        self.assertEquals(response.status_code, 200)

    def test_logged_in(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password="test"))
        response = self.client.get('/accounts/password_change/')
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/accounts/password_reset/')
        self.assertEquals(response.status_code, 200)


class ApiViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.site = LearningSiteFactory()
        self.repository = ArchivalRepositoryFactory()

    def test_anonymous(self):
        # views succeed
        response = self.client.get('/api/site/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEquals(the_json[0]['id'], self.site.id)

        response = self.client.get('/api/repository/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        the_json = loads(response.content.decode('utf-8'))
        self.assertEquals(the_json[0]['id'], self.repository.id)

        # update fails
        response = self.client.post('/api/site/',
                                    {'id': self.site.id, 'title': 'Foo'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

    def test_update(self):
        self.client.login(username=self.user.username, password='test')
        data = {
            'id': self.site.id, 'title': 'Foo',
            'latlng': {'lat': 5, 'lng': 6},
            'established': '2008-01-01', 'defunct': '2009-01-01'
        }
        response = self.client.post(
            '/api/site/',
            dumps(data),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 201)


class TestUpdateView(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()

        site = LearningSiteFactory()
        self.url = reverse('site-update-view', kwargs={'pk': site.id})

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_non_editor(self):
        user = UserFactory()
        self.client.login(username=user.username, password='test')
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_editor(self):
        editor = UserFactory()
        editor.groups.add(GroupFactory(name='Editor'))
        self.client.login(username=editor.username, password='test')
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)


class TestDigitalObjectCreateView(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()
        self.url = reverse('digital-object-create-view',
                           kwargs={'parent': self.site.id})

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_non_editor(self):
        user = UserFactory()
        self.client.login(username=user.username, password='test')
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_editor(self):
        editor = UserFactory()
        editor.groups.add(GroupFactory(name='Editor'))
        self.client.login(username=editor.username, password='test')
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        view = DigitalObjectCreateView()
        view.request = RequestFactory()
        view.request.method = 'GET'
        view.kwargs = {'parent': self.site.id}
        view.object = None

        ctx = view.get_context_data()
        self.assertEquals(ctx['parent'], self.site)


class TestLearningSiteGalleryView(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()
        self.url = reverse('site-gallery-view',
                           kwargs={'parent': self.site.id})

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
