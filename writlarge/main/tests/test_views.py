from json import loads, dumps

from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.test.utils import override_settings
from django.urls.base import reverse

from writlarge.main.models import ArchivalCollection
from writlarge.main.tests.factories import (
    UserFactory, LearningSiteFactory, ArchivalRepositoryFactory,
    GroupFactory, ArchivalCollectionFactory, FootnoteFactory)
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

    @override_settings(GOOGLE_MAP_API='123456')
    def test_django_settings(self):
        request = RequestFactory()
        request.user = UserFactory()

        ctx = django_settings(request)
        self.assertEquals(ctx['settings']['GOOGLE_MAP_API'], '123456')
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
        view.parent = self.site
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


class TestAddRemoveCollection(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()
        self.collection = ArchivalCollectionFactory()
        self.link_url = reverse('collection-link-view',
                                kwargs={'parent': self.site.id})
        self.unlink_url = reverse('collection-unlink-view',
                                  kwargs={'parent': self.site.id,
                                          'pk': self.collection.id})

    def test_anonymous(self):
        response = self.client.get(self.link_url)
        self.assertEquals(response.status_code, 302)

        response = self.client.post(self.unlink_url)
        self.assertEquals(response.status_code, 302)

    def test_link_and_unlink(self):
        editor = UserFactory()
        editor.groups.add(GroupFactory(name='Editor'))
        self.client.login(username=editor.username, password='test')

        response = self.client.get(self.link_url)
        self.assertEquals(response.status_code, 200)

        response = self.client.post(self.link_url,
                                    {'collection': self.collection.id})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.site.archivalcollection_set.count(), 1)
        self.assertEquals(
            self.site.archivalcollection_set.first(), self.collection)

        response = self.client.get(self.unlink_url)
        self.assertEquals(response.status_code, 200)
        response = self.client.post(self.unlink_url, {})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.site.archivalcollection_set.count(), 0)


class TestArchivalCollectionCreateView(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()
        self.repository = ArchivalRepositoryFactory()

        self.url = reverse('collection-create-view',
                           kwargs={'parent': self.site.id})

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        user = UserFactory()
        self.client.login(username=user.username, password='test')
        response = self.client.post(self.url)
        self.assertEquals(response.status_code, 302)

    def test_create(self):
        editor = UserFactory()
        editor.groups.add(GroupFactory(name='Editor'))
        self.client.login(username=editor.username, password='test')

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        data = {
            'title': 'New', 'description': '', 'finding_aid_url': '',
            'repository': '{}'.format(self.repository.id),
            'linear_feet': '', 'inclusive_start_date_month': '1',
            'inclusive_start_date_day': '1',
            'inclusive_start_date_year': '2018',
            'inclusive_end_date_month': '1',
            'inclusive_end_date_day': '1',
            'inclusive_end_date_year': '2018'
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 302)

        collection = ArchivalCollection.objects.get(title='New')
        self.assertTrue(collection.learning_sites.filter(
            title=self.site.title).exists())


class TestArchivalCollectionUpdateView(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()
        self.collection = ArchivalCollectionFactory()
        self.collection.learning_sites.add(self.site)

        self.url = reverse('collection-edit-view',
                           kwargs={'parent': self.site.id,
                                   'pk': self.collection.id})

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        user = UserFactory()
        self.client.login(username=user.username, password='test')
        response = self.client.post(self.url)
        self.assertEquals(response.status_code, 302)

    def test_update(self):
        editor = UserFactory()
        editor.groups.add(GroupFactory(name='Editor'))
        self.client.login(username=editor.username, password='test')

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        data = {
            'title': 'Updated', 'description': '', 'finding_aid_url': '',
            'linear_feet': '', 'inclusive_start_date_month': '1',
            'inclusive_start_date_day': '1',
            'inclusive_start_date_year': '2018',
            'inclusive_end_date_month': '1',
            'inclusive_end_date_day': '1',
            'inclusive_end_date_year': '2018'
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 302)

        self.collection.refresh_from_db()
        self.assertEquals(self.collection.title, 'Updated')


class TestArchivalCollectionDeleteView(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()
        self.collection = ArchivalCollectionFactory()
        self.collection.learning_sites.add(self.site)

        self.url = reverse('collection-delete-view',
                           kwargs={'parent': self.site.id,
                                   'pk': self.collection.id})

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        user = UserFactory()
        self.client.login(username=user.username, password='test')
        response = self.client.post(self.url)
        self.assertEquals(response.status_code, 302)

    def test_delete(self):
        editor = UserFactory()
        editor.groups.add(GroupFactory(name='Editor'))
        self.client.login(username=editor.username, password='test')

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        response = self.client.post(self.url, {})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.site.archivalcollection_set.count(), 0)


class TestFootnoteViews(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()
        self.footnote = FootnoteFactory()
        self.site.footnotes.add(self.footnote)
        self.create_url = reverse('footnote-create-view',
                                  kwargs={'parent': self.site.id})
        self.edit_url = reverse('footnote-edit-view',
                                kwargs={'parent': self.site.id,
                                        'pk': self.footnote.id})
        self.delete_url = reverse('footnote-delete-view',
                                  kwargs={'parent': self.site.id,
                                          'pk': self.footnote.id})

    def test_anonymous(self):
        response = self.client.get(self.create_url)
        self.assertEquals(response.status_code, 302)
        response = self.client.get(self.edit_url)
        self.assertEquals(response.status_code, 302)
        response = self.client.get(self.delete_url)
        self.assertEquals(response.status_code, 302)

    def test_non_editor(self):
        user = UserFactory()
        self.client.login(username=user.username, password='test')
        response = self.client.get(self.create_url)
        self.assertEquals(response.status_code, 302)
        response = self.client.get(self.edit_url)
        self.assertEquals(response.status_code, 302)
        response = self.client.get(self.delete_url)
        self.assertEquals(response.status_code, 302)

    def test_editor(self):
        editor = UserFactory()
        editor.groups.add(GroupFactory(name='Editor'))
        self.client.login(username=editor.username, password='test')
        response = self.client.get(self.create_url)
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.edit_url)
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.delete_url)
        self.assertEquals(response.status_code, 200)

        response = self.client.post(self.create_url, {'note': 'Something'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.site.footnotes.count(), 2)

        response = self.client.post(self.edit_url, {'note': 'Changed'})
        self.assertEquals(response.status_code, 302)
        self.footnote.refresh_from_db()
        self.assertEquals(self.footnote.note, 'Changed')

        response = self.client.post(self.delete_url, {})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.site.footnotes.count(), 1)
        self.assertEquals(self.site.footnotes.first().note, 'Something')
