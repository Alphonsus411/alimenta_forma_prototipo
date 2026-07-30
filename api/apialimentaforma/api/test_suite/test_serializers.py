from django.contrib.auth.models import User
from django.test import TestCase

from api.models import Course, Registration, UserType
from api.serializer import CourseSerializer, MarkSerializer, RegistrationSerializer


class DomainSerializerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        teacher_role = UserType.objects.get_or_create(category='p')[0]
        cls.teacher = User.objects.create_user(username='serializer_teacher')
        cls.teacher.profile.userType = teacher_role
        cls.teacher.profile.save(update_fields=('userType',))
        cls.student = User.objects.create_user(username='serializer_student')
        cls.course = Course.objects.create(
            title='Higiene', detail='Curso', classes=3, teacher=cls.teacher
        )

    def test_course_teacher_is_read_only(self):
        serializer = CourseSerializer(data={
            'title': 'Cocina', 'detail': 'Curso', 'classes': 2,
            'teacher': self.student.id,
            'category': self.course.category_id, 'modality': 'online',
            'duration_hours': '3.00', 'start_date': '2026-09-01',
            'end_date': '2026-09-02', 'capacity': 12,
            'location': 'Campus', 'price': '0.00', 'objectives': 'Aprender.',
            'requirements': 'Sin requisitos',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('teacher', serializer.validated_data)

    def test_registration_student_is_read_only(self):
        serializer = RegistrationSerializer(data={
            'course': self.course.id, 'student': self.teacher.id,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('student', serializer.validated_data)

    def test_mark_rejects_values_outside_scale(self):
        Registration.objects.create(course=self.course, student=self.student)
        serializer = MarkSerializer(data={
            'course': self.course.id, 'student': self.student.id, 'mark_1': 11,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('mark_1', serializer.errors)
