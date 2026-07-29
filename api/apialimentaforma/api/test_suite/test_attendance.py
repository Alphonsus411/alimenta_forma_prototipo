from datetime import date
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from api.models import Attendance, Course, Registration, UserType
from api.services.attendance import AttendanceDomainError, validate_attendance_context


class AttendanceServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        teacher_role, _ = UserType.objects.get_or_create(category='p')
        student_role, _ = UserType.objects.get_or_create(category='s')
        cls.teacher = User.objects.create_user(username='attendance_teacher')
        cls.teacher.profile.userType = teacher_role
        cls.teacher.profile.save(update_fields=('userType',))
        cls.student = User.objects.create_user(username='attendance_student')
        cls.student.profile.userType = student_role
        cls.student.profile.save(update_fields=('userType',))

    def make_course(self, classes=5):
        return Course.objects.create(
            title=f'Curso de {classes} clases', detail='Prueba', classes=classes,
            teacher=self.teacher,
        )

    def test_attendance_requires_a_registration(self):
        course = self.make_course()

        with self.assertRaisesMessage(AttendanceDomainError, 'No existe una matrícula'):
            Attendance.objects.create(course=course, student=self.student, present=True)

    def test_duplicate_registration_is_reported_explicitly(self):
        course = self.make_course()
        duplicated_queryset = Mock()
        duplicated_queryset.count.return_value = 2

        with patch('api.services.attendance.Registration.objects.filter', return_value=duplicated_queryset):
            with self.assertRaisesMessage(AttendanceDomainError, 'más de una matrícula'):
                validate_attendance_context(course.id, self.student.id)

    def test_present_does_not_accept_null(self):
        course = self.make_course()
        attendance = Attendance(course=course, student=self.student, present=None)

        with self.assertRaises(ValidationError) as context:
            attendance.full_clean()

        self.assertIn('present', context.exception.message_dict)

    def test_course_must_have_a_valid_total_of_classes(self):
        course = self.make_course()
        Registration.objects.create(course=course, student=self.student)
        course.classes = 0

        with patch('api.services.attendance.Course.objects.get', return_value=course):
            with self.assertRaisesMessage(AttendanceDomainError, 'al menos una clase'):
                validate_attendance_context(course.id, self.student.id)

    def test_exact_twenty_percent_keeps_registration_enabled(self):
        course = self.make_course(classes=5)
        registration = Registration.objects.create(course=course, student=self.student)

        Attendance.objects.create(
            course=course, student=self.student, date=date(2026, 1, 1), present=False
        )

        registration.refresh_from_db()
        self.assertTrue(registration.enabled)

    def test_more_than_twenty_percent_disables_registration(self):
        course = self.make_course(classes=5)
        registration = Registration.objects.create(course=course, student=self.student)
        for day in (1, 2):
            Attendance.objects.create(
                course=course, student=self.student, date=date(2026, 1, day), present=False
            )

        registration.refresh_from_db()
        self.assertFalse(registration.enabled)

    def test_editing_attendance_recalculates_registration(self):
        course = self.make_course(classes=4)
        registration = Registration.objects.create(course=course, student=self.student)
        attendance = Attendance.objects.create(
            course=course, student=self.student, date=date(2026, 2, 1), present=False
        )
        registration.refresh_from_db()
        self.assertFalse(registration.enabled)

        attendance.present = True
        attendance.save(update_fields=('present',))

        registration.refresh_from_db()
        self.assertTrue(registration.enabled)

    def test_deleting_attendance_recalculates_registration(self):
        course = self.make_course(classes=4)
        registration = Registration.objects.create(course=course, student=self.student)
        attendance = Attendance.objects.create(
            course=course, student=self.student, date=date(2026, 3, 1), present=False
        )
        registration.refresh_from_db()
        self.assertFalse(registration.enabled)

        attendance.delete()

        registration.refresh_from_db()
        self.assertTrue(registration.enabled)
