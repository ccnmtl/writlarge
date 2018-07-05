from json import loads, dumps

from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.test.utils import override_settings
from django.urls.base import reverse

from writlarge.main.forms import ConnectionForm
from writlarge.main.models import ArchivalCollection, LearningSite
from writlarge.main.serializers import LearningSiteSerializer
from writlarge.main.tests.factories import (
    UserFactory, LearningSiteFactory, ArchivalRepositoryFactory,
    GroupFactory, ArchivalCollectionFactory, FootnoteFactory,
    LearningSiteRelationshipFactory)
from writlarge.main.views import (
    django_settings, DigitalObjectCreateView, ConnectionCreateView)


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


class DetailViewTests(TestCase):

    def test_learning_site_detail(self):
        site = LearningSiteFactory()
        url = reverse('site-detail-view', kwargs={'pk': site.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_archival_collection_detail(self):
        collection = ArchivalCollectionFactory()
        url = reverse('collection-detail-view', kwargs={'pk': collection.id})
        response = self.client.get(url)
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

    def test_create(self):
        self.client.login(username=self.user.username, password='test')
        data = {
            'title': 'Foo',
            'place': [{'title': 'Bar', 'latlng': {'lat': 5, 'lng': 6}}]
        }
        response = self.client.post(
            '/api/site/',
            dumps(data),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 201)

        site = LearningSite.objects.get(title='Foo')
        self.assertEquals(site.place.first().title, 'Bar')

    def test_update(self):
        self.client.login(username=self.user.username, password='test')
        data = {
            'id': self.site.id, 'title': 'Foo',
            'place': [{'title': 'Bar', 'latlng': {'lat': 5, 'lng': 6}}],
            'established': '', 'defunct': ''
        }
        response = self.client.put(
            '/api/site/{}/'.format(self.site.id),
            dumps(data),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.site.refresh_from_db()
        self.assertEquals(self.site.title, 'Foo')

    def test_family(self):
        parent = LearningSiteFactory()
        sib = LearningSiteFactory()
        sib2 = LearningSiteFactory()

        LearningSiteRelationshipFactory(site_one=parent, site_two=sib)
        LearningSiteRelationshipFactory(site_one=sib2, site_two=parent)

        family = LearningSiteSerializer().get_family(parent)
        self.assertEquals(len(family), 2)
        self.assertEquals(family[0]['id'], sib.id)
        self.assertEquals(family[0]['relationship'], 'associate')
        self.assertEquals(family[1]['id'], sib2.id)
        self.assertEquals(family[1]['relationship'], 'associate')


class TestLearningSiteUpdateView(TestCase):

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


class TestLearningSiteDeleteView(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()

        grp = GroupFactory(name='Editor')

        self.editor = UserFactory()
        self.editor.groups.add(grp)

        self.creator = UserFactory()
        self.creator.groups.add(grp)

        self.site = LearningSiteFactory(created_by=self.creator)
        self.url = reverse('site-delete-view', kwargs={'pk': self.site.id})

    def test_restricted_access(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        user = UserFactory()  # random user
        self.client.login(username=user.username, password='test')
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username=self.editor.username, password='test')
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

    def test_creator(self):
        self.client.login(username=self.creator.username, password='test')
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        response = self.client.post(self.url)
        self.assertEquals(response.status_code, 302)

        self.assertTrue(LearningSite.objects.count(), 0)


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
            'collection_title': 'New', 'description': '',
            'finding_aid_url': '',
            'repository': '{}'.format(self.repository.id),
            'linear_feet': '',
            'inclusive-start-millenium1': '2',
            'inclusive-start-century1': '0',
            'inclusive-start-decade1': '0',
            'inclusive-start-year1': '0',
            'inclusive-end-millenium1': '2',
            'inclusive-end-century1': '0',
            'inclusive-end-decade1': '0',
            'inclusive-end-year1': '1',
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 302)

        collection = ArchivalCollection.objects.get(collection_title='New')
        self.assertTrue(collection.learning_sites.filter(
            title=self.site.title).exists())
        self.assertEquals(collection.inclusive_start.edtf_format, '2000')
        self.assertEquals(collection.inclusive_end.edtf_format, '2001')


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
            'repository': self.collection.repository.id,
            'repository_title': 'foobarbaz',
            'title': 'Bar', 'latlng': 'SRID=4326;POINT(1 1)',
            'collection_title': 'Updated', 'description': '',
            'finding_aid_url': '',
            'linear_feet': '',
            'inclusive-start-millenium1': '2',
            'inclusive-start-century1': '0',
            'inclusive-start-decade1': '0',
            'inclusive-start-year1': '0',
            'inclusive-end-millenium1': '2',
            'inclusive-end-century1': '0',
            'inclusive-end-decade1': '0',
            'inclusive-end-year1': '1',
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 302)

        self.collection.refresh_from_db()
        self.assertEquals(self.collection.collection_title, 'Updated')
        self.assertEquals(self.collection.inclusive_start.edtf_format, '2000')
        self.assertEquals(self.collection.inclusive_end.edtf_format, '2001')

        self.collection.repository.refresh_from_db()
        self.assertEquals(self.collection.repository.title, 'foobarbaz')
        self.collection.repository.place.refresh_from_db()
        self.assertEquals(self.collection.repository.place.title, 'Bar')
        self.assertEquals(self.collection.repository.place.latitude(), 1.0)
        self.assertEquals(self.collection.repository.place.longitude(), 1.0)


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


class TestArchivalCollectionListView(TestCase):

    def setUp(self):
        self.user = UserFactory(username='editor')
        self.coll1 = ArchivalCollectionFactory(collection_title='alpha')
        self.coll2 = ArchivalCollectionFactory(collection_title='beta')

    def test_search_by_title(self):
        url = "{}?q=beta&rid=".format(reverse('archival-collections'))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['page_obj'].object_list), 1)
        self.assertEquals(
            response.context['page_obj'].object_list[0], self.coll2)

        self.assertEquals(response.context['query'], 'beta')
        self.assertEquals(
            response.context['base_url'], '/collections/?q=beta&rid=&page=')
        self.assertEquals(response.context['repositories'].count(), 1)
        self.assertTrue(
            self.coll2.repository in response.context['repositories'])

    def test_search_by_repository(self):
        url = "{}?q=&rid={}".format(reverse('archival-collections'),
                                    self.coll1.repository.id)

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['page_obj'].object_list), 1)
        self.assertEquals(
            response.context['page_obj'].object_list[0], self.coll1)

        self.assertEquals(response.context['query'], '')
        self.assertEquals(response.context['repositories'].count(), 1)
        self.assertTrue(
            self.coll1.repository in response.context['repositories'])

    def test_empty_search(self):
        url = reverse('archival-collections')

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['page_obj'].object_list), 2)
        self.assertTrue(
            self.coll1 in response.context['page_obj'].object_list)
        self.assertTrue(
            self.coll2 in response.context['page_obj'].object_list)
        self.assertTrue(
            self.coll1.repository in response.context['repositories'])
        self.assertTrue(
            self.coll2.repository in response.context['repositories'])


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

        response = self.client.post(self.create_url,
                                    {'ordinal': 2, 'note': 'Something'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.site.footnotes.count(), 2)

        response = self.client.post(self.edit_url,
                                    {'ordinal': 2, 'note': 'Changed'})
        self.assertEquals(response.status_code, 302)
        self.footnote.refresh_from_db()
        self.assertEquals(self.footnote.note, 'Changed')

        response = self.client.post(self.delete_url, {})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(self.site.footnotes.count(), 1)
        self.assertEquals(self.site.footnotes.first().note, 'Something')


class DisplayDateViewTest(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()
        self.url = reverse('display-date-view')

    def test_post(self):
        # no ajax
        self.assertEquals(self.client.post(self.url).status_code, 405)

        # no_data(self):
        response = self.client.post(self.url,
                                    {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertTrue(the_json['success'])

        # success
        response = self.client.post(self.url,
                                    {'millenium1': '1', 'century1': '6',
                                     'decade1': '7', 'year1': '3',
                                     'month1': '', 'day1': ''},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertTrue(the_json['success'])
        self.assertEquals(the_json['display'], '1673')

        # invalid date
        response = self.client.post(self.url,
                                    {'millenium1': '13', 'century1': '6',
                                     'decade1': '7', 'year1': '3',
                                     'month1': '', 'day1': ''},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertFalse(the_json['success'])

        self.assertTrue('Please specify a valid date' in the_json['msg'])
        self.assertTrue('millenium1' in the_json['msg'])


class SearchViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory(username='editor')
        self.site1 = LearningSiteFactory(title='foo', created_by=self.user)
        self.site2 = LearningSiteFactory(title='bar')

    def test_search_by_title(self):
        url = "{}?q=bar".format(reverse('search-view'))
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['page_obj'].object_list), 1)
        self.assertEquals(
            response.context['page_obj'].object_list[0], self.site2)

        self.assertEquals(response.context['query'], 'bar')
        self.assertEquals(
            response.context['base_url'], '/search/?q=bar&page=')

    def test_search_by_creator(self):
        url = "{}?q={}".format(reverse('search-view'), self.user.username)

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['page_obj'].object_list), 1)
        self.assertEquals(
            response.context['page_obj'].object_list[0], self.site1)

        self.assertEquals(response.context['query'], self.user.username)

    def test_empty_search(self):
        url = reverse('search-view')

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['page_obj'].object_list), 2)
        self.assertTrue(
            self.site1 in response.context['page_obj'].object_list)
        self.assertTrue(
            self.site2 in response.context['page_obj'].object_list)


class ConnectionCreateViewTest(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()
        self.parent = LearningSiteFactory()

    def test_get_form(self):
        view = ConnectionCreateView()
        view.parent = self.parent
        view.request = RequestFactory()
        view.request.method = 'GET'

        frm = view.get_form()
        self.assertEquals(frm.fields['site'].queryset.count(), 1)
        self.assertEquals(frm.fields['site'].queryset[0], self.site)

    def test_form_valid_associates(self):
        site = LearningSiteFactory()
        frm = ConnectionForm()
        frm.cleaned_data = {
            'connection_type': 'associate',
            'site': site
        }
        view = ConnectionCreateView()
        view.parent = self.parent
        view.form_valid(frm)

        self.assertTrue(len(self.parent.associates()), 1)
        self.assertEquals(self.parent.associates()[0], site)


class ConnectionDeleteViewTest(TestCase):

    def setUp(self):
        self.site = LearningSiteFactory()
        self.parent = LearningSiteFactory()

        editor = UserFactory()
        editor.groups.add(GroupFactory(name='Editor'))
        self.client.login(username=editor.username, password='test')

    def test_remove_associate(self):
        LearningSiteRelationshipFactory(
            site_one=self.parent, site_two=self.site)
        url = reverse('connection-delete-view', kwargs={
            'parent': self.parent.pk,
            'type': 'associate',
            'pk': self.site.pk})
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)
        self.assertTrue(self.site not in self.parent.associates())
