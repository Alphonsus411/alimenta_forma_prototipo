from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from pathlib import Path

from api.models import Announcement, Attendance, Course, Mark, Registration


class ProfileSignalTests(TestCase):
    def test_creating_user_creates_empty_student_profile(self):
        user = User.objects.create_user(username='student', password='safe-password')

        self.assertEqual(user.profile.userType.category, 's')
        self.assertEqual(user.profile.location, '')


class MarkTests(TestCase):
    def test_average_includes_zero_marks(self):
        teacher = User.objects.create_user(username='teacher')
        student = User.objects.create_user(username='student')
        course = Course.objects.create(
            title='Seguridad alimentaria', detail='Curso', classes=3, teacher=teacher
        )

        mark = Mark.objects.create(course=course, student=student, mark_1=0, mark_2=10)

        self.assertEqual(mark.average, 5)


class AttendanceTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher')
        self.student = User.objects.create_user(username='student')
        self.course = Course.objects.create(
            title='Manipulación', detail='Curso', classes=4, teacher=self.teacher
        )
        self.registration = Registration.objects.create(
            course=self.course, student=self.student
        )

    def test_registration_is_disabled_above_twenty_percent_absence(self):
        attendance = Attendance.objects.create(
            course=self.course, student=self.student, present=False
        )

        attendance.updateRegistrationEnabledStatus()

        self.registration.refresh_from_db()
        self.assertFalse(self.registration.enabled)

    def test_zero_class_course_is_rejected_when_updating_attendance(self):
        self.course.classes = 0
        self.course.save()
        attendance = Attendance.objects.create(
            course=self.course, student=self.student, present=False
        )

        with self.assertRaisesMessage(ValueError, 'al menos una clase'):
            attendance.updateRegistrationEnabledStatus()


class AnnouncementTests(TestCase):
    def test_string_representation_uses_uploaded_filename(self):
        owner = User.objects.create_user(username='company')
        announcement = Announcement.objects.create(
            owner=owner,
            detail=SimpleUploadedFile('oferta.pdf', b'contenido'),
        )

        uploaded_path = Path(str(announcement))
        self.assertTrue(uploaded_path.stem.startswith('oferta'))
        self.assertEqual(uploaded_path.suffix, '.pdf')
