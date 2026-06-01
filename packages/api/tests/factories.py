import factory

from api.models.permission import Permission
from api.models.project import Project
from api.models.role import Role
from api.models.user import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


class RoleFactory(factory.Factory):
    class Meta:
        model = Role

    name = factory.Sequence(lambda n: f'ROLE_{n}')


class PermissionFactory(factory.Factory):
    class Meta:
        model = Permission

    name = factory.Sequence(lambda n: f'permission_{n}')


class ProjectFactory(factory.Factory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f'Project Artificial Intelligence {n}')
    created_by = 1
