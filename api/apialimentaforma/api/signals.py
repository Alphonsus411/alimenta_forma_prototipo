from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save, pre_save
from .models import Attendance, Profile
from .roles import ROLE_NAMES
from .services.attendance import recalculate_registration_status, validate_attendance_context

@receiver(post_save, sender=Profile)
def synchronize_user_role_group(sender, instance, **kwargs):
    """Mantiene un único grupo de rol coherente con la categoría del perfil."""
    role_groups = {
        category: Group.objects.get_or_create(name=name)[0]
        for category, name in ROLE_NAMES.items()
    }
    instance.user.groups.remove(*role_groups.values())
    instance.user.groups.add(role_groups[instance.userType.category])


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
