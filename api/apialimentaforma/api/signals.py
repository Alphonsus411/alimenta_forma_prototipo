from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save, pre_save
from .models import Attendance, Profile
from .services.attendance import recalculate_registration_status, validate_attendance_context

@receiver (post_save, sender=Profile)
def add_user_to_students_group (sender, instance, created, **kwargs):
    if created:
        try:
            group1 = Group.objects.get(name='estudiante')
        except Group.DoesNotExist:
            group1 = Group.objects.create(name='estudiante')
            group2 = Group.objects.create(name='profesor')
            group3 = Group.objects.create(name='empresa')
            group4 = Group.objects.create(name='administrativo')
        instance.user.groups.add(group1)


@receiver(pre_save, sender=Attendance)
def validate_attendance_and_remember_previous_pair(sender, instance, **kwargs):
    """Valida el contexto y conserva el par anterior si una edición lo cambia."""
    validate_attendance_context(instance.course_id, instance.student_id)
    instance._previous_attendance_pair = None
    if instance.pk:
        previous = Attendance.objects.filter(pk=instance.pk).values_list(
            'course_id', 'student_id'
        ).first()
        current = (instance.course_id, instance.student_id)
        if previous and previous != current:
            instance._previous_attendance_pair = previous


@receiver(post_save, sender=Attendance)
def recalculate_after_attendance_save(sender, instance, **kwargs):
    previous = getattr(instance, '_previous_attendance_pair', None)
    if previous:
        recalculate_registration_status(*previous)
    recalculate_registration_status(instance.course_id, instance.student_id)


@receiver(post_delete, sender=Attendance)
def recalculate_after_attendance_delete(sender, instance, **kwargs):
    recalculate_registration_status(instance.course_id, instance.student_id)
