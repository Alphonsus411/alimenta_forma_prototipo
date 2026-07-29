from django.contrib.auth.models import Group, User
from django.test import TestCase

from api.models import UserType
from api.roles import ADMIN, COMPANY, ROLE_NAMES, STUDENT, TEACHER


class RoleGroupSignalTests(TestCase):
    def assert_user_has_only_role_group(self, user, category):
        assigned_role_groups = set(
            user.groups.filter(name__in=ROLE_NAMES.values()).values_list('name', flat=True)
        )
        self.assertEqual(assigned_role_groups, {ROLE_NAMES[category]})

    def test_empty_database_creates_every_group_and_assigns_student(self):
        self.assertFalse(Group.objects.exists())

        user = User.objects.create_user(username='estudiante')

        self.assertSetEqual(
            set(Group.objects.values_list('name', flat=True)),
            set(ROLE_NAMES.values()),
        )
        self.assert_user_has_only_role_group(user, STUDENT)

    def test_partially_created_groups_are_completed(self):
        Group.objects.create(name=ROLE_NAMES[TEACHER])
        Group.objects.create(name=ROLE_NAMES[COMPANY])

        user = User.objects.create_user(username='grupos_parciales')

        self.assertSetEqual(
            set(Group.objects.values_list('name', flat=True)),
            set(ROLE_NAMES.values()),
        )
        self.assert_user_has_only_role_group(user, STUDENT)

    def test_each_profile_category_assigns_its_canonical_group(self):
        for category in (ADMIN, COMPANY, TEACHER, STUDENT):
            with self.subTest(category=category):
                user = User.objects.create_user(username=f'usuario_{category}')
                user.profile.userType = UserType.objects.get_or_create(category=category)[0]
                user.profile.save(update_fields=('userType',))

                self.assert_user_has_only_role_group(user, category)

    def test_category_change_removes_incompatible_role_groups(self):
        user = User.objects.create_user(username='cambia_rol')
        unrelated_group = Group.objects.create(name='boletin')
        user.groups.add(
            unrelated_group,
            Group.objects.get(name=ROLE_NAMES[ADMIN]),
            Group.objects.get(name=ROLE_NAMES[COMPANY]),
        )

        user.profile.userType = UserType.objects.get_or_create(category=TEACHER)[0]
        user.profile.save(update_fields=('userType',))

        self.assert_user_has_only_role_group(user, TEACHER)
        self.assertTrue(user.groups.filter(pk=unrelated_group.pk).exists())
