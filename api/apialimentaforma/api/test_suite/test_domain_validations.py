from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from api.models import Attendance, Course, Mark, Offer, Registration, UserType


class DomainValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.roles = {
            category: UserType.objects.get_or_create(category=category)[0]
            for category in ('p', 's')
        }
        cls.teacher = cls.make_user('profesor', 'p')
        cls.student = cls.make_user('estudiante', 's')
        cls.other_student = cls.make_user('otro_estudiante', 's')
        cls.course = Course.objects.create(
            title='Manipulación de alimentos',
            detail='Curso de prueba',
            classes=4,
            teacher=cls.teacher,
        )

    @classmethod
    def make_user(cls, username, role):
        user = User.objects.create_user(username=username)
        user.profile.userType = cls.roles[role]
        user.profile.save(update_fields=('userType',))
        return user

    def test_course_requires_positive_number_of_classes(self):
        course = Course(title='Sin clases', detail='Inválido', classes=0, teacher=self.teacher)

        with self.assertRaises(ValidationError) as context:
            course.full_clean()

        self.assertIn('classes', context.exception.message_dict)

    def test_offer_price_cannot_be_negative(self):
        offer = Offer(price=-1, detail='Inválida', userType=self.roles['s'])

        with self.assertRaises(ValidationError) as context:
            offer.full_clean()

        self.assertIn('price', context.exception.message_dict)

    def test_marks_use_zero_to_ten_scale(self):
        for value in (-1, 11):
            with self.subTest(value=value):
                mark = Mark(course=self.course, student=self.student, mark_1=value)
                with self.assertRaises(ValidationError) as context:
                    mark.full_clean()
                self.assertIn('mark_1', context.exception.message_dict)

    def test_course_teacher_must_have_teacher_role(self):
        course = Course(
            title='Profesor inválido', detail='Inválido', classes=1, teacher=self.student
        )

        with self.assertRaises(ValidationError) as context:
            course.full_clean()

        self.assertIn('teacher', context.exception.message_dict)

    def test_course_records_require_student_role(self):
        invalid_records = (
            Registration(course=self.course, student=self.teacher),
            Attendance(
                course=self.course,
                student=self.teacher,
                date=date(2026, 7, 29),
            ),
            Mark(course=self.course, student=self.teacher, mark_1=8),
        )

        for record in invalid_records:
            with self.subTest(model=type(record).__name__):
                with self.assertRaises(ValidationError) as context:
                    record.full_clean()
                self.assertIn('student', context.exception.message_dict)

    def test_only_one_registration_per_course_and_student(self):
        Registration.objects.create(course=self.course, student=self.student)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Registration.objects.create(course=self.course, student=self.student)

    def test_only_one_mark_per_course_and_student(self):
        Mark.objects.create(course=self.course, student=self.student, mark_1=8)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Mark.objects.create(course=self.course, student=self.student, mark_1=9)

    def test_attendance_identity_is_course_student_and_date(self):
        first_date = date(2026, 7, 29)
        Attendance.objects.create(
            course=self.course, student=self.student, date=first_date, present=True
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Attendance.objects.create(
                course=self.course, student=self.student, date=first_date, present=False
            )

        next_day = Attendance.objects.create(
            course=self.course,
            student=self.student,
            date=first_date + timedelta(days=1),
            present=True,
        )
        self.assertIsNotNone(next_day.pk)

    def test_registration_has_correct_verbose_name(self):
        self.assertEqual(Registration._meta.verbose_name, 'Inscripción')
