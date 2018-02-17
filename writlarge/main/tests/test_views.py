from json import loads, dumps

from django.test import TestCase
from django.test.client import Client

from writlarge.main.tests.factories import (
    UserFactory, LearningSiteFactory, ArchivalRepositoryFactory)


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
