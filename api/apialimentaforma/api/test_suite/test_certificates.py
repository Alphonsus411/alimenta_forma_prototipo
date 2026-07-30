from datetime import date, timedelta
from decimal import Decimal
import uuid

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.models import (
    Attendance,
    Certificate,
    CompletionEvaluation,
    Content,
    Course,
    CourseApprovalRule,
    CourseCompletion,
    CourseLesson,
    LessonCompletion,
    Mark,
    Registration,
)
from api.services.completions import evaluate_registration


class CompletionFixtureMixin:
    def setUp(self):
        self.teacher = User.objects.create_user(username='docente')
        self.student = User.objects.create_user(
            username='alumna', first_name='Ana', last_name='Alba'
        )
        self.course = Course.objects.create(
            title='Higiene verificable', detail='Curso', classes=2,
            teacher=self.teacher, status=Course.Status.CLOSED,
        )
        self.registration = Registration.objects.create(
            course=self.course, student=self.student
        )
        self.rule = CourseApprovalRule.objects.create(
            course=self.course, minimum_attendance_percentage=Decimal('75'),
            minimum_grade=Decimal('5'), require_content_completion=True,
        )
        content = Content.objects.create(title='Tema', comment='Contenido')
        self.lesson = CourseLesson.objects.create(
            course=self.course, content=content, order=1
        )

    def add_passing_evidence(self):
        for offset in range(2):
            Attendance.objects.create(
                course=self.course, student=self.student,
                date=date(2026, 7, 1) + timedelta(days=offset), present=True,
            )
        Mark.objects.create(
            course=self.course, student=self.student, mark_1=8, mark_2=6
        )
        LessonCompletion.objects.create(
            registration=self.registration, lesson=self.lesson
        )


class CompletionServiceTests(CompletionFixtureMixin, APITestCase):

    def test_approved_result_issues_one_certificate_idempotently(self):
        self.add_passing_evidence()

        first = evaluate_registration(self.registration.id)
        second = evaluate_registration(self.registration.id)

        self.assertEqual(first.outcome, CourseCompletion.Outcome.PASSED)
        self.assertEqual(second.pk, first.pk)
        self.assertEqual(second.revision, 1)
        self.assertEqual(CompletionEvaluation.objects.count(), 1)
        self.assertEqual(Certificate.objects.count(), 1)

    def test_failed_result_reports_low_grade_and_incomplete_content(self):
        Attendance.objects.create(
            course=self.course, student=self.student, present=True
        )
        Mark.objects.create(course=self.course, student=self.student, mark_1=4)

        completion = evaluate_registration(self.registration.id)

        self.assertEqual(completion.outcome, CourseCompletion.Outcome.FAILED)
        self.assertIn('calificacion_insuficiente', completion.failure_reasons)
        self.assertIn('asistencia_insuficiente', completion.failure_reasons)
        self.assertIn('contenidos_incompletos', completion.failure_reasons)
        self.assertFalse(Certificate.objects.exists())

    def test_attendance_threshold_is_configurable_per_course(self):
        self.rule.minimum_grade = None
        self.rule.require_content_completion = False
        self.rule.minimum_attendance_percentage = Decimal('60')
        self.rule.save()
        Attendance.objects.create(
            course=self.course, student=self.student, present=True
        )

        completion = evaluate_registration(self.registration.id)

        self.assertEqual(completion.attendance_percentage, Decimal('50.00'))
        self.assertEqual(completion.failure_reasons, ['asistencia_insuficiente'])

    def test_reevaluation_preserves_previous_result_and_issues_certificate(self):
        completion = evaluate_registration(self.registration.id)
        self.assertEqual(completion.outcome, CourseCompletion.Outcome.FAILED)
        self.add_passing_evidence()

        completion = evaluate_registration(self.registration.id)

        self.assertEqual(completion.outcome, CourseCompletion.Outcome.PASSED)
        self.assertEqual(completion.revision, 2)
        self.assertEqual(
            list(completion.evaluations.values_list('outcome', flat=True)),
            [CourseCompletion.Outcome.FAILED, CourseCompletion.Outcome.PASSED],
        )
        self.assertTrue(Certificate.objects.filter(completion=completion).exists())

    def test_database_rejects_duplicate_completion_for_registration(self):
        completion = evaluate_registration(self.registration.id)

        with self.assertRaises(IntegrityError), transaction.atomic():
            CourseCompletion.objects.create(
                registration=self.registration, course=self.course,
                outcome=CourseCompletion.Outcome.FAILED,
                attendance_percentage=0, content_completion_percentage=0,
                rule_snapshot={}, evidence_snapshot={}, input_fingerprint='x' * 64,
            )
        self.assertTrue(CourseCompletion.objects.filter(pk=completion.pk).exists())


class CertificateApiTests(CompletionFixtureMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.add_passing_evidence()
        self.completion = evaluate_registration(self.registration.id)
        self.certificate = self.completion.certificate
        self.other_student = User.objects.create_user(username='otra')
        self.client = APIClient()

    def test_student_can_consult_and_download_own_certificate(self):
        self.client.force_authenticate(self.student)

        listing = self.client.get(reverse('certificate-list'))
        download = self.client.get(
            reverse('certificate-download', args=[self.certificate.public_id])
        )

        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listing.data), 1)
        self.assertEqual(download.status_code, status.HTTP_200_OK)
        self.assertTrue(download['Content-Disposition'].startswith('attachment;'))

    def test_anonymous_and_other_student_cannot_access_private_certificate(self):
        detail_url = reverse('certificate-detail', args=[self.certificate.public_id])
        self.assertEqual(
            self.client.get(detail_url).status_code, status.HTTP_403_FORBIDDEN
        )
        self.client.force_authenticate(self.other_student)
        self.assertEqual(
            self.client.get(detail_url).status_code, status.HTTP_404_NOT_FOUND
        )

    def test_public_verification_returns_only_minimum_data(self):
        response = self.client.get(
            reverse('certificate-verify', args=[self.certificate.public_id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'vigente')
        self.assertNotIn('holder_name', response.data)
        self.assertNotIn('student', response.data)

    def test_public_verification_distinguishes_revoked_and_missing(self):
        self.certificate.revoked_at = self.certificate.issued_at
        self.certificate.revocation_reason = 'Corrección administrativa'
        self.certificate.save()

        revoked = self.client.get(
            reverse('certificate-verify', args=[self.certificate.public_id])
        )
        missing = self.client.get(
            reverse('certificate-verify', args=[uuid.uuid4()])
        )

        self.assertEqual(revoked.data['status'], 'revocado')
        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(missing.data, {'status': 'inexistente'})
