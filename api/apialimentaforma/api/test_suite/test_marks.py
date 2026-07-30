from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Course, Mark, Registration, UserType


class MarkAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        teacher_role = UserType.objects.get_or_create(category='p')[0]
        cls.teacher = User.objects.create_user(username='mark_teacher')
        cls.teacher.profile.userType = teacher_role
        cls.teacher.profile.save(update_fields=('userType',))
        cls.student = User.objects.create_user(username='mark_student')
        cls.other_student = User.objects.create_user(username='other_mark_student')
        cls.course = Course.objects.create(
            title='Pastelería', detail='Curso', classes=3, teacher=cls.teacher
        )
        Registration.objects.create(course=cls.course, student=cls.student)
        cls.mark = Mark.objects.create(
            course=cls.course, student=cls.student, mark_1=8, mark_2=10
        )

    def test_teacher_updates_mark_and_response_recalculates_average(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.patch(
            reverse('mark-detail', args=[self.mark.id]), {'mark_1': 6}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['average'], '8.0')

    def test_student_list_is_isolated_from_other_users(self):
        self.client.force_authenticate(self.other_student)

        response = self.client.get(reverse('mark-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_teacher_cannot_mark_a_student_not_registered_in_course(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(reverse('mark-list'), {
            'course': self.course.id, 'student': self.other_student.id, 'mark_1': 7,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No existe una matrícula', response.data['student'][0])
