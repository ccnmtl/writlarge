from django.conf import settings
from django.contrib.auth.models import Group


class EditorMapper(object):
    """ if the user is in one of the specified wind affil groups,
        give the user Editor privileges in the environment """

    def __init__(self):
        if not hasattr(settings, 'WIND_STAFF_MAPPER_GROUPS'):
            self.groups = []
        else:
            self.groups = settings.WIND_STAFF_MAPPER_GROUPS

    def map(self, user, affils):
        for affil in affils:
            if affil in self.groups:
                (grp, created) = Group.objects.get_or_create(name='Editor')
                user.groups.add(grp)
                return
