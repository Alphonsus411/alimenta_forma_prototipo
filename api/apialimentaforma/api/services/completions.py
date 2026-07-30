import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.utils import timezone

from api.models import (
    Attendance,
    Certificate,
    CompletionEvaluation,
    Course,
    CourseApprovalRule,
    CourseCompletion,
    LessonCompletion,
    Mark,
    Registration,
)


class CompletionDomainError(ValueError):
    """Indica que la matrícula todavía no se puede evaluar."""


def _percentage(numerator, denominator):
    if denominator == 0:
        return Decimal('100.00')
    return (Decimal(numerator) * 100 / Decimal(denominator)).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )


@transaction.atomic
def evaluate_registration(registration_id):
    """Evalúa una matrícula sin duplicar revisiones ante las mismas entradas."""
    registration = Registration.objects.select_for_update().select_related(
        'course', 'student'
    ).get(pk=registration_id)
    course = registration.course
    try:
        rule = course.approval_rule
    except CourseApprovalRule.DoesNotExist as error:
        raise CompletionDomainError('El curso no tiene reglas de aprobación configuradas.') from error

    attendance_total = course.classes
    present_count = Attendance.objects.filter(
        course=course, student=registration.student, present=True
    ).count()
    attendance_percentage = _percentage(present_count, attendance_total)

    mark = Mark.objects.filter(course=course, student=registration.student).first()
    final_grade = mark.average if mark else None
    lesson_ids = list(course.lessons.order_by('id').values_list('id', flat=True))
    completed_lesson_ids = list(LessonCompletion.objects.filter(
        registration=registration, lesson_id__in=lesson_ids
    ).order_by('lesson_id').values_list('lesson_id', flat=True))
    content_percentage = _percentage(len(completed_lesson_ids), len(lesson_ids))

    rule_snapshot = {
        'minimum_attendance_percentage': (
            str(rule.minimum_attendance_percentage)
            if rule.minimum_attendance_percentage is not None else None
        ),
        'minimum_grade': str(rule.minimum_grade) if rule.minimum_grade is not None else None,
        'require_content_completion': rule.require_content_completion,
    }
    evidence_snapshot = {
        'course_classes': attendance_total,
        'present_count': present_count,
        'attendance_percentage': str(attendance_percentage),
        'final_grade': str(final_grade) if final_grade is not None else None,
        'lesson_ids': lesson_ids,
        'completed_lesson_ids': completed_lesson_ids,
        'content_completion_percentage': str(content_percentage),
    }
    failure_reasons = []
    if (
        rule.minimum_attendance_percentage is not None
        and attendance_percentage < rule.minimum_attendance_percentage
    ):
        failure_reasons.append('asistencia_insuficiente')
    if rule.minimum_grade is not None and (
        final_grade is None or final_grade < rule.minimum_grade
    ):
        failure_reasons.append('calificacion_insuficiente')
    if rule.require_content_completion and content_percentage < Decimal('100'):
        failure_reasons.append('contenidos_incompletos')
    outcome = (
        CourseCompletion.Outcome.FAILED if failure_reasons
        else CourseCompletion.Outcome.PASSED
    )
    fingerprint = hashlib.sha256(json.dumps(
        {'rule': rule_snapshot, 'evidence': evidence_snapshot},
        sort_keys=True, separators=(',', ':'),
    ).encode()).hexdigest()

    completion = CourseCompletion.objects.filter(registration=registration).first()
    if completion and completion.input_fingerprint == fingerprint:
        return completion

    now = timezone.now()
    revision = completion.revision + 1 if completion else 1
    values = {
        'course': course,
        'outcome': outcome,
        'failure_reasons': failure_reasons,
        'attendance_percentage': attendance_percentage,
        'final_grade': final_grade,
        'content_completion_percentage': content_percentage,
        'rule_snapshot': rule_snapshot,
        'evidence_snapshot': evidence_snapshot,
        'input_fingerprint': fingerprint,
        'revision': revision,
        'evaluated_at': now,
    }
    if completion:
        for field, value in values.items():
            setattr(completion, field, value)
        completion.save(update_fields=(*values.keys(),))
    else:
        completion = CourseCompletion.objects.create(registration=registration, **values)

    CompletionEvaluation.objects.create(
        completion=completion, revision=revision, outcome=outcome,
        failure_reasons=failure_reasons, rule_snapshot=rule_snapshot,
        evidence_snapshot=evidence_snapshot, input_fingerprint=fingerprint,
        evaluated_at=now,
    )

    certificate = Certificate.objects.filter(completion=completion).first()
    if outcome == CourseCompletion.Outcome.PASSED and course.status == Course.Status.CLOSED:
        Certificate.objects.get_or_create(
            completion=completion,
            defaults={
                'holder_name': registration.student.get_full_name() or registration.student.username,
                'course_title': course.title,
            },
        )
    elif certificate and certificate.revoked_at is None:
        certificate.revoked_at = now
        certificate.revocation_reason = 'Resultado invalidado por una reevaluación.'
        certificate.save(update_fields=('revoked_at', 'revocation_reason'))
    return completion
