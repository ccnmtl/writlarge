from django.test.client import RequestFactory
from django.test.testcases import TestCase

from writlarge.main.mixins import LearningSiteSearchMixin
from writlarge.main.models import LearningSite
from writlarge.main.tests.factories import LearningSiteFactory


class LearningSiteSearchMixinTest(TestCase):

    def setUp(self):
        self.site1 = LearningSiteFactory(title='Site Alpha')
        self.site2 = LearningSiteFactory(title='Site Beta')
        self.site3 = LearningSiteFactory(title='Site Gamma')
        self.site3.tags.add('red')

    def test_filter(self):
        mixin = LearningSiteSearchMixin()
        mixin.request = RequestFactory().get('/', {'q': 'Alpha'})
        qs = mixin.filter(LearningSite.objects.all())
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), self.site1)

    def test_process_query(self):
        mixin = LearningSiteSearchMixin()

        all = LearningSite.objects.all()
        qs = mixin._process_query(qs=all, q='site')
        self.assertEquals(qs.count(), 3)

        qs = mixin._process_query(qs=all, q='Alpha')
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), self.site1)

        qs = mixin._process_query(
            qs=all, q='category:{}'.format(self.site2.category.first().name))
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), self.site2)

        qs = mixin._process_query(qs=all, q='tag:red')
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), self.site3)

    def test_tokenize(self):
        mixin = LearningSiteSearchMixin()

        t = mixin._tokenize('some search terms')
        self.assertEquals(next(t), ('STRING', 'some'))
        self.assertEquals(next(t), ('STRING', 'search'))
        self.assertEquals(next(t), ('STRING', 'terms'))

        t = mixin._tokenize('"abc"')
        self.assertEquals(next(t), ('STRING', 'abc'))

        t = mixin._tokenize('"abc" "def"')
        self.assertEquals(next(t), ('STRING', 'abc'))
        self.assertEquals(next(t), ('STRING', 'def'))

        t = mixin._tokenize('category:foo')
        self.assertEquals(next(t), ('CATEGORY', 'foo'))

        t = mixin._tokenize('tag:bar')
        self.assertEquals(next(t), ('TAG', 'bar'))

        t = mixin._tokenize('category:foo baz')
        self.assertEquals(next(t), ('CATEGORY', 'foo'))
        self.assertEquals(next(t), ('STRING', 'baz'))

        q = 'some "a b" search category:foo tag:xyz terms'
        t = mixin._tokenize(q)
        self.assertEquals(next(t), ('STRING', 'some'))
        self.assertEquals(next(t), ('STRING', 'a b'))
        self.assertEquals(next(t), ('STRING', 'search'))
        self.assertEquals(next(t), ('CATEGORY', 'foo'))
        self.assertEquals(next(t), ('TAG', 'xyz'))
        self.assertEquals(next(t), ('STRING', 'terms'))
