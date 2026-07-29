from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Course, Registration, UserType


class RegistrationAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        teacher_role = UserType.objects.get_or_create(category='p')[0]
        cls.teacher = User.objects.create_user(username='registration_teacher')
        cls.teacher.profile.userType = teacher_role
        cls.teacher.profile.save(update_fields=('userType',))
        cls.student = User.objects.create_user(username='registration_student')
        cls.other_student = User.objects.create_user(username='other_registration_student')
        cls.course = Course.objects.create(
            title='Cocina', detail='Curso', classes=3, teacher=cls.teacher
        )
        cls.other_registration = Registration.objects.create(
            course=cls.course, student=cls.other_student
        )

    def test_student_creates_and_reads_only_own_registration(self):
        self.client.force_authenticate(self.student)
        created = self.client.post(
            reverse('registration-list'), {'course': self.course.id}, format='json'
        )

        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data['student'], self.student.id)
        listed = self.client.get(reverse('registration-list'))
        self.assertEqual([item['id'] for item in listed.data], [created.data['id']])
        self.assertEqual(
            self.client.get(
                reverse('registration-detail', args=[self.other_registration.id])
            ).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_duplicate_registration_returns_validation_error(self):
        Registration.objects.create(course=self.course, student=self.student)
        self.client.force_authenticate(self.student)

        response = self.client.post(
            reverse('registration-list'), {'course': self.course.id}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
