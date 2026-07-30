from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from api.models import Content, Course, CourseCategory, CourseLesson, UserType


class CourseMetadataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        teacher_role = UserType.objects.get_or_create(category='p')[0]
        cls.teacher = User.objects.create_user(username='metadata_teacher')
        cls.teacher.profile.userType = teacher_role
        cls.teacher.profile.save(update_fields=('userType',))
        cls.category = CourseCategory.objects.get_or_create(name='Cocina')[0]

    def course(self, **overrides):
        values = {
            'title': 'Cocina segura', 'detail': 'Ficha completa', 'classes': 4,
            'teacher': self.teacher, 'category': self.category,
            'modality': Course.Modality.BLENDED, 'duration_hours': Decimal('12.50'),
            'start_date': date(2026, 9, 1), 'end_date': date(2026, 9, 5),
            'capacity': 20, 'location': 'Aula 2 y campus virtual',
            'price': Decimal('49.90'), 'objectives': 'Trabajar de forma segura.',
            'requirements': 'Calzado de seguridad.',
        }
        values.update(overrides)
        return Course(**values)

    def test_rejects_inverted_dates(self):
        course = self.course(start_date=date(2026, 9, 6))
        with self.assertRaisesMessage(ValidationError, 'fecha de fin'):
            course.full_clean()

    def test_rejects_invalid_capacity_duration_and_price(self):
        for field, value in (('capacity', 0), ('duration_hours', 0), ('price', -1)):
            with self.subTest(field=field):
                with self.assertRaises(ValidationError):
                    self.course(**{field: value}).full_clean()

    def test_lessons_are_unique_and_ordered_per_course(self):
        course = self.course()
        course.save()
        first = Content.objects.create(title='Primera', comment='Inicio')
        second = Content.objects.create(title='Segunda', comment='Final')
        CourseLesson.objects.create(course=course, content=second, order=2)
        CourseLesson.objects.create(course=course, content=first, order=1)
        self.assertEqual(list(course.lessons.values_list('content__title', flat=True)), ['Primera', 'Segunda'])
        duplicate = CourseLesson(course=course, content=second, order=1)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_status_transition_matrix(self):
        allowed = Course.ALLOWED_STATUS_TRANSITIONS
        all_statuses = {value for value, _ in Course.Status.choices}
        for origin in all_statuses:
            for target in all_statuses - {origin}:
                with self.subTest(origin=origin, target=target):
                    course = self.course(status=origin)
                    course.save()
                    course.status = target
                    if target in allowed[origin]:
                        course.full_clean()
                    else:
                        with self.assertRaises(ValidationError):
                            course.full_clean()
                    course.delete()
