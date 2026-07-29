from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import SAFE_METHODS, BasePermission


ADMIN = 'a'
COMPANY = 'c'
TEACHER = 'p'
STUDENT = 's'


def has_role(user, role):
  """Comprueba el rol de dominio sin asumir que el usuario tiene perfil."""
  if not user or not user.is_authenticated:
    return False
  if role == ADMIN and (user.is_staff or user.is_superuser):
    return True
  try:
    return user.profile.userType.category == role
  except (AttributeError, ObjectDoesNotExist):
    return False


def is_admin(user):
  return has_role(user, ADMIN)


class ReadOnlyOrAdmin(BasePermission):
  """Permite lectura pública y reserva las escrituras al administrador."""

  def has_permission(self, request, view):
    return request.method in SAFE_METHODS or is_admin(request.user)


class IsAuthenticatedProfileOwnerOrAdmin(BasePermission):
  def has_permission(self, request, view):
    return request.user.is_authenticated

  def has_object_permission(self, request, view, obj):
    return is_admin(request.user) or obj.user_id == request.user.id


class IsCompanyAnnouncementOwnerOrAdmin(BasePermission):
  def has_permission(self, request, view):
    if request.method in SAFE_METHODS:
      return True
    return is_admin(request.user) or has_role(request.user, COMPANY)

  def has_object_permission(self, request, view, obj):
    if request.method in SAFE_METHODS:
      return True
    return is_admin(request.user) or (
      has_role(request.user, COMPANY) and obj.owner_id == request.user.id
    )


class IsTeacherCourseOwnerOrAdmin(BasePermission):
  def has_permission(self, request, view):
    if request.method in SAFE_METHODS:
      return True
    return is_admin(request.user) or has_role(request.user, TEACHER)

  def has_object_permission(self, request, view, obj):
    if request.method in SAFE_METHODS:
      return True
    return is_admin(request.user) or obj.teacher_id == request.user.id


class IsRegistrationOwnerOrAdmin(BasePermission):
  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if request.method == 'POST':
      return has_role(request.user, STUDENT)
    return True

  def has_object_permission(self, request, view, obj):
    return is_admin(request.user) or obj.student_id == request.user.id


class IsTeacherOfCourseOrStudentOrAdmin(BasePermission):
  """Protege notas/asistencias: el alumno lee las suyas y el profesor gestiona su curso."""

  def has_permission(self, request, view):
    if not request.user.is_authenticated:
      return False
    if request.method in SAFE_METHODS:
      return True
    return is_admin(request.user) or has_role(request.user, TEACHER)

  def has_object_permission(self, request, view, obj):
    if is_admin(request.user):
      return True
    if request.method in SAFE_METHODS and obj.student_id == request.user.id:
      return True
    return has_role(request.user, TEACHER) and obj.course.teacher_id == request.user.id
