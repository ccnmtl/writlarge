from django.contrib.auth.models import User, Group, Permission
import factory


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: "user%03d" % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')

    @factory.post_generation
    def group(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.groups.add(extracted)


class GroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = Group

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            lst = list(Permission.objects.filter(codename__in=extracted))
            self.permissions.add(*lst)
