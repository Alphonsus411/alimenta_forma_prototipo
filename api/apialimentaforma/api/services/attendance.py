from django.db import transaction

from api.models import Attendance, Course, Registration


class AttendanceDomainError(ValueError):
    """Indica que no se puede calcular la regularidad de una matrícula."""


def validate_attendance_context(course_id, student_id):
    """Comprueba que el curso es válido y que hay exactamente una matrícula."""
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist as error:
        raise AttendanceDomainError('El curso de la asistencia no existe.') from error
    if course.classes <= 0:
        raise AttendanceDomainError('El curso debe tener al menos una clase.')

    registrations = Registration.objects.filter(course_id=course_id, student_id=student_id)
    count = registrations.count()
    if count == 0:
        raise AttendanceDomainError('No existe una matrícula para el alumno y el curso.')
    if count > 1:
        raise AttendanceDomainError('Existe más de una matrícula para el alumno y el curso.')
    return course, registrations


@transaction.atomic
def recalculate_registration_status(course_id, student_id):
    """Activa la matrícula salvo que las ausencias superen el veinte por ciento."""
    course, registrations = validate_attendance_context(course_id, student_id)
    registration = registrations.select_for_update().get()
    absences = Attendance.objects.filter(
        course_id=course_id, student_id=student_id, present=False
    ).count()
    enabled = absences * 100 <= course.classes * 20
    if registration.enabled != enabled:
        registration.enabled = enabled
        registration.save(update_fields=('enabled',))
    return registration
