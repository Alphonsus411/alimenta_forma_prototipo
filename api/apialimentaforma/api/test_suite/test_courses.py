from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Course, UserType


class CourseAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        role = UserType.objects.get_or_create(category='p')[0]
        cls.teacher = User.objects.create_user(username='course_teacher')
        cls.teacher.profile.userType = role
        cls.teacher.profile.save(update_fields=('userType',))
        cls.other_teacher = User.objects.create_user(username='other_course_teacher')
        cls.other_teacher.profile.userType = role
        cls.other_teacher.profile.save(update_fields=('userType',))
        cls.course = Course.objects.create(
            title='Manipulación', detail='Inicial', classes=3, teacher=cls.teacher
        )

    def test_teacher_completes_authorized_crud(self):
        self.client.force_authenticate(self.teacher)
        created = self.client.post(reverse('course-list'), {
            'title': 'Nutrición', 'detail': 'Nuevo', 'classes': 4,
        }, format='json')
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data['teacher'], self.teacher.id)

        detail_url = reverse('course-detail', args=[created.data['id']])
        updated = self.client.patch(detail_url, {'detail': 'Actualizado'}, format='json')
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data['detail'], 'Actualizado')
        self.assertEqual(self.client.delete(detail_url).status_code, status.HTTP_204_NO_CONTENT)

    def test_teacher_cannot_update_another_users_course(self):
        self.client.force_authenticate(self.other_teacher)

        response = self.client.patch(
            reverse('course-detail', args=[self.course.id]), {'title': 'Ajeno'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
