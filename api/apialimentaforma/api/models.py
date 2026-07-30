from decimal import Decimal
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save
from django.utils import timezone

from .roles import ROLE_CHOICES, ROLE_NAMES, STUDENT, TEACHER
from .validators import (
  announcement_upload_to,
  announcement_validators,
  content_document_upload_to,
  content_image_upload_to,
  content_video_upload_to,
  cv_validators,
  document_validators,
  image_validators,
  profile_cv_upload_to,
  profile_image_upload_to,
  video_validators,
)


def validate_user_role(user, expected_role, field_name):
  """Valida el rol de dominio almacenado en el perfil de un usuario."""
  try:
    role = user.profile.userType.category
  except (Profile.DoesNotExist, UserType.DoesNotExist):
    role = None
  if role != expected_role:
    role_name = ROLE_NAMES[expected_role]
    raise ValidationError({field_name: f'El usuario debe tener el rol {role_name}.'})

# TIPOS DE USUARIO ---------------------------------------------

class UserType (models.Model):
  categoryChoices = ROLE_CHOICES
  category = models.CharField(max_length=1, choices=categoryChoices, default=STUDENT, verbose_name='Categoria')

  def __str__(self):
    return self.category
  
  class Meta:
    verbose_name= 'Categoria'
    verbose_name_plural= 'Categorias'

# PERFIL DE CADA USUARIO -----------------------------------------

class Profile (models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name= 'profile', verbose_name= 'Usuario')
  location = models.CharField(max_length=150, blank=True, default='', verbose_name= 'Ciudad')
  image = models.ImageField(
    upload_to=profile_image_upload_to, validators=image_validators,
    blank=True, null=True, verbose_name='Imagen'
  )
  phone = models.CharField(max_length= 15, blank=True, default='', verbose_name= 'Telefono')
  description = models.CharField(max_length= 500, blank=True, default='', verbose_name= 'Descripcion')
  userType = models.ForeignKey(UserType, on_delete= models.CASCADE, verbose_name= 'Categoria')
  cv = models.FileField(
    upload_to=profile_cv_upload_to, validators=cv_validators,
    blank=True, null=True, verbose_name='CV'
  )

  def __str__(self):
    return self.user.username

  class Meta:
    verbose_name = 'perfil'
    verbose_name_plural = 'perfiles'
    ordering = ['-id']

def create_user_profile (sender, instance, created, **kwargs):
    if created:
        default_user_type, _ = UserType.objects.get_or_create(category=STUDENT)
        Profile.objects.create(user=instance, userType=default_user_type)
        
def save_user_profile (sender, instance, **Kwargs):
    instance.profile.save()
    
post_save.connect (create_user_profile, sender=User)
post_save.connect (save_user_profile, sender=User)

# TIPOS DE MEMBRESIA QUE PUEDE HABER -------------------------------------

class Offer (models.Model):
  price = models.IntegerField(validators=[MinValueValidator(0)], verbose_name= 'Precio')
  detail = models.CharField(max_length= 500, verbose_name= 'Detalle')
  userType = models.ForeignKey(UserType, on_delete= models.CASCADE, verbose_name= 'Categoria')

  def __str__(self):
    return self.userType.category

  class Meta:
    verbose_name = 'Membresia'
    verbose_name_plural = 'Membresias'
    constraints = [
      models.CheckConstraint(check=models.Q(price__gte=0), name='offer_price_non_negative'),
    ]

# ANUNCIOS DE LOS MIEMBROS, RESERVADO PARA EMPRESAS --------------------------------

class Announcement (models.Model):
  detail = models.FileField(
    upload_to=announcement_upload_to, validators=announcement_validators,
    verbose_name='Detalle'
  )
  owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')

  def __str__(self):
    return self.detail.name

  class Meta:  
    verbose_name = 'Anuncio'
    verbose_name_plural = 'Anuncios'

# CONTENIDO DE LOS CURSOS, ESTO SE GENERA SI SE REQUIERE ---------------------------------

class Content (models.Model):
  title = models.CharField(max_length=150, verbose_name= 'Tutulo')
  comment = models.CharField(max_length=500, verbose_name= 'Comentario')
  img = models.ImageField(
    upload_to=content_image_upload_to, validators=image_validators,
    blank=True, null=True, verbose_name='Material grafico'
  )
  doc = models.FileField(
    upload_to=content_document_upload_to, validators=document_validators,
    blank=True, null=True, verbose_name='Material escrito'
  )
  videos = models.FileField(
    upload_to=content_video_upload_to, validators=video_validators,
    blank=True, null=True, verbose_name='Material de video'
  )

  def __str__(self):
    return self.title

  class Meta:
    verbose_name = 'Contenido'
    verbose_name_plural = 'Contenidos'

# CURSOS DISPONIBLES, LOS COLOCAN LOS PROFESORES ---------------------------------------------

class CourseCategory(models.Model):
  name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
  active = models.BooleanField(default=True, verbose_name='Activa')

  def __str__(self):
    return self.name

  class Meta:
    verbose_name = 'Categoría de curso'
    verbose_name_plural = 'Categorías de curso'
    ordering = ('name',)


def get_default_course_category():
  """Categoría segura para altas internas antiguas; la API exige una explícita."""
  return CourseCategory.objects.get_or_create(name='Manipulación de alimentos')[0].pk


class Course(models.Model):
  class Modality(models.TextChoices):
    IN_PERSON = 'presencial', 'Presencial'
    ONLINE = 'online', 'Online'
    BLENDED = 'mixta', 'Mixta'

  class Status(models.TextChoices):
    DRAFT = 'borrador', 'Borrador'
    REVIEW = 'revision', 'En revisión'
    PUBLISHED = 'publicado', 'Publicado'
    ENROLLMENT_CLOSED = 'inscripcion_cerrada', 'Inscripción cerrada'
    IN_PROGRESS = 'desarrollo', 'En desarrollo'
    FINISHED = 'finalizado', 'Finalizado'
    CLOSED = 'cerrado', 'Cerrado'
    CANCELLED = 'cancelado', 'Cancelado'

  ALLOWED_STATUS_TRANSITIONS = {
    Status.DRAFT: {Status.REVIEW, Status.CANCELLED},
    Status.REVIEW: {Status.PUBLISHED, Status.DRAFT, Status.CANCELLED},
    Status.PUBLISHED: {Status.ENROLLMENT_CLOSED, Status.CANCELLED},
    Status.ENROLLMENT_CLOSED: {Status.IN_PROGRESS, Status.CANCELLED},
    Status.IN_PROGRESS: {Status.FINISHED, Status.CANCELLED},
    Status.FINISHED: {Status.CLOSED},
    Status.CLOSED: set(),
    Status.CANCELLED: set(),
  }

  title = models.CharField(max_length=150, verbose_name='Título')
  detail = models.CharField(max_length=500, verbose_name='Detalle')
  classes = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Clases')
  teacher = models.ForeignKey(User, verbose_name='Profesor', on_delete=models.CASCADE)
  category = models.ForeignKey(CourseCategory, on_delete=models.PROTECT, related_name='courses', default=get_default_course_category, verbose_name='Categoría')
  modality = models.CharField(max_length=12, choices=Modality.choices, default=Modality.IN_PERSON, verbose_name='Modalidad')
  duration_hours = models.DecimalField(max_digits=6, decimal_places=2, default=1, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Duración (horas)')
  start_date = models.DateField(default=timezone.localdate, verbose_name='Fecha de inicio')
  end_date = models.DateField(default=timezone.localdate, verbose_name='Fecha de fin')
  capacity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='Aforo')
  location = models.CharField(max_length=300, default='Pendiente de actualizar', verbose_name='Ubicación o acceso')
  price = models.DecimalField(max_digits=8, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))], verbose_name='Precio')
  objectives = models.TextField(default='Pendiente de actualizar', verbose_name='Objetivos')
  requirements = models.TextField(default='Sin requisitos', verbose_name='Requisitos')
  status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='Estado de publicación')

  def __str__(self):
    return self.title

  def clean(self):
    super().clean()
    validate_user_role(self.teacher, TEACHER, 'teacher')
    errors = {}
    if self.start_date and self.end_date and self.start_date > self.end_date:
      errors['end_date'] = 'La fecha de fin no puede ser anterior a la fecha de inicio.'
    if self.pk:
      previous = Course.objects.filter(pk=self.pk).values_list('status', flat=True).first()
      if previous and previous != self.status and self.status not in self.ALLOWED_STATUS_TRANSITIONS.get(previous, set()):
        errors['status'] = f'No se permite pasar de {previous} a {self.status}.'
    if errors:
      raise ValidationError(errors)

  class Meta:
    verbose_name = 'Curso'
    verbose_name_plural = 'Cursos'
    constraints = [
      models.CheckConstraint(check=models.Q(classes__gt=0), name='course_classes_positive'),
      models.CheckConstraint(check=models.Q(duration_hours__gt=0), name='course_duration_positive'),
      models.CheckConstraint(check=models.Q(capacity__gt=0), name='course_capacity_positive'),
      models.CheckConstraint(check=models.Q(price__gte=0), name='course_price_non_negative'),
      models.CheckConstraint(check=models.Q(end_date__gte=models.F('start_date')), name='course_dates_ordered'),
    ]


class CourseLesson(models.Model):
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Curso')
  content = models.ForeignKey(Content, on_delete=models.PROTECT, related_name='course_lessons', verbose_name='Contenido')
  order = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name='Orden')

  def __str__(self):
    return f'{self.course}: {self.order}. {self.content}'

  class Meta:
    verbose_name = 'Lección de curso'
    verbose_name_plural = 'Lecciones de curso'
    ordering = ('order', 'id')
    constraints = [
      models.UniqueConstraint(fields=('course', 'order'), name='unique_course_lesson_order'),
      models.CheckConstraint(check=models.Q(order__gt=0), name='course_lesson_order_positive'),
    ]

# REGISTRO DE USUARIOS ----------------------------------------

class Registration (models.Model):
  course = models.ForeignKey(Course, on_delete= models.CASCADE, verbose_name= 'Curso')
  student = models.ForeignKey(User, related_name= 'student_registration', on_delete= models.CASCADE, verbose_name= 'Alumno')
  enabled = models.BooleanField(default= True, verbose_name= 'Alumno regular')

  def __str__(self):
    return f'{self.student.username} - {self.course.title}'

  def clean(self):
    super().clean()
    validate_user_role(self.student, STUDENT, 'student')
  
  class Meta:
    verbose_name = 'Inscripción'
    verbose_name_plural = 'Inscripciones'
    constraints = [
      models.UniqueConstraint(fields=('course', 'student'), name='unique_registration_course_student'),
    ]

# ASISTENCIAS A LOS CURSOS ------------------------------------------

class Attendance (models.Model):
  course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name= 'Curso')
  student = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'attendance', verbose_name= 'Alumno')
  date = models.DateField(default=timezone.localdate, verbose_name='Fecha')
  # Una asistencia siempre representa uno de dos estados: presente o ausente.
  present = models.BooleanField(default=False, verbose_name='Presente')

  def __str__(self):
    return f'Asistencia - {self.id}'

  def clean(self):
    super().clean()
    validate_user_role(self.student, STUDENT, 'student')

  class Meta:
    verbose_name = 'Asistencia'
    verbose_name_plural = 'Asistencias'
    constraints = [
      models.UniqueConstraint(
        fields=('course', 'student', 'date'), name='unique_attendance_course_student_date'
      ),
    ]

# CALIFICACIONES DE LOS CURSOS EN LOS CURSOS -----------------------------------

class Mark (models.Model):
  course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Curso')
  student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': ROLE_NAMES[STUDENT]}, verbose_name='Estudiante')
  mark_validators = [MinValueValidator(0), MaxValueValidator(10)]
  average_validators = [MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('10'))]
  mark_1 = models.PositiveIntegerField(null=True, blank=True, validators=mark_validators, verbose_name='Nota 1')
  mark_2 = models.PositiveIntegerField(null=True, blank=True, validators=mark_validators, verbose_name='Nota 2')
  mark_3 = models.PositiveIntegerField(null=True, blank=True, validators=mark_validators, verbose_name='Nota 3')
  average = models.DecimalField(
    max_digits=3, decimal_places=1, null=True, blank=True, validators=average_validators,
    verbose_name='Promedio'
  )
  
  def __str__(self):
    return str(self.course)

  def clean(self):
    super().clean()
    validate_user_role(self.student, STUDENT, 'student')
  
  # Calcular el promedio de las notas
  def calculate_average (self):
    marks = [self.mark_1, self.mark_2, self.mark_3]
    valid_marks = [mark for mark in marks if mark is not None]
    if valid_marks:
      return sum(valid_marks) / len (valid_marks)
    return None
  
  def save (self, *args, **kwargs):
    self.average = self.calculate_average()
    super().save(*args, **kwargs)
      
  class Meta:
    verbose_name = 'Nota'
    verbose_name_plural = 'Notas'
    constraints = [
      models.UniqueConstraint(fields=('course', 'student'), name='unique_mark_course_student'),
      models.CheckConstraint(
        check=models.Q(mark_1__isnull=True) | models.Q(mark_1__range=(0, 10)),
        name='mark_1_between_0_and_10',
      ),
      models.CheckConstraint(
        check=models.Q(mark_2__isnull=True) | models.Q(mark_2__range=(0, 10)),
        name='mark_2_between_0_and_10',
      ),
      models.CheckConstraint(
        check=models.Q(mark_3__isnull=True) | models.Q(mark_3__range=(0, 10)),
        name='mark_3_between_0_and_10',
      ),
    ]


class CourseApprovalRule(models.Model):
  """Criterios de aprobación publicados para una edición concreta."""

  course = models.OneToOneField(
    Course, on_delete=models.CASCADE, related_name='approval_rule', verbose_name='Curso'
  )
  minimum_attendance_percentage = models.DecimalField(
    max_digits=5, decimal_places=2, null=True, blank=True,
    validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
    verbose_name='Asistencia mínima (%)',
  )
  minimum_grade = models.DecimalField(
    max_digits=3, decimal_places=1, null=True, blank=True,
    validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('10'))],
    verbose_name='Calificación mínima',
  )
  require_content_completion = models.BooleanField(
    default=False, verbose_name='Exigir todos los contenidos'
  )
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = 'Regla de aprobación'
    verbose_name_plural = 'Reglas de aprobación'
    constraints = [
      models.CheckConstraint(
        check=models.Q(minimum_attendance_percentage__isnull=True) | models.Q(
          minimum_attendance_percentage__range=(0, 100)
        ), name='approval_attendance_between_0_and_100'
      ),
      models.CheckConstraint(
        check=models.Q(minimum_grade__isnull=True) | models.Q(minimum_grade__range=(0, 10)),
        name='approval_grade_between_0_and_10'
      ),
    ]


class LessonCompletion(models.Model):
  """Evidencia de que una matrícula terminó un contenido del curso."""

  registration = models.ForeignKey(
    Registration, on_delete=models.CASCADE, related_name='completed_lessons',
    verbose_name='Matrícula'
  )
  lesson = models.ForeignKey(
    CourseLesson, on_delete=models.CASCADE, related_name='registration_completions',
    verbose_name='Lección'
  )
  completed_at = models.DateTimeField(default=timezone.now, verbose_name='Finalizado el')

  class Meta:
    verbose_name = 'Contenido finalizado'
    verbose_name_plural = 'Contenidos finalizados'
    constraints = [
      models.UniqueConstraint(
        fields=('registration', 'lesson'), name='unique_registration_lesson_completion'
      ),
    ]


class CourseCompletion(models.Model):
  class Outcome(models.TextChoices):
    PASSED = 'aprobado', 'Aprobado'
    FAILED = 'suspenso', 'Suspenso'

  registration = models.OneToOneField(
    Registration, on_delete=models.CASCADE, related_name='completion', verbose_name='Matrícula'
  )
  course = models.ForeignKey(
    Course, on_delete=models.PROTECT, related_name='completions', verbose_name='Curso'
  )
  outcome = models.CharField(max_length=10, choices=Outcome.choices, verbose_name='Resultado')
  failure_reasons = models.JSONField(default=list, blank=True, verbose_name='Motivos')
  attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2)
  final_grade = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
  content_completion_percentage = models.DecimalField(max_digits=5, decimal_places=2)
  rule_snapshot = models.JSONField(verbose_name='Regla aplicada')
  evidence_snapshot = models.JSONField(verbose_name='Evidencias aplicadas')
  input_fingerprint = models.CharField(max_length=64, verbose_name='Huella de entradas')
  revision = models.PositiveIntegerField(default=1)
  evaluated_at = models.DateTimeField(default=timezone.now)

  class Meta:
    verbose_name = 'Finalización de curso'
    verbose_name_plural = 'Finalizaciones de curso'
    constraints = [
      models.UniqueConstraint(
        fields=('registration', 'course'), name='unique_completion_registration_course'
      ),
    ]


class CompletionEvaluation(models.Model):
  """Copia inmutable de cada resultado distinto calculado por el servicio."""

  completion = models.ForeignKey(
    CourseCompletion, on_delete=models.CASCADE, related_name='evaluations'
  )
  revision = models.PositiveIntegerField()
  outcome = models.CharField(max_length=10, choices=CourseCompletion.Outcome.choices)
  failure_reasons = models.JSONField(default=list, blank=True)
  rule_snapshot = models.JSONField()
  evidence_snapshot = models.JSONField()
  input_fingerprint = models.CharField(max_length=64)
  evaluated_at = models.DateTimeField(default=timezone.now)

  class Meta:
    ordering = ('revision',)
    constraints = [
      models.UniqueConstraint(
        fields=('completion', 'revision'), name='unique_completion_evaluation_revision'
      ),
      models.UniqueConstraint(
        fields=('completion', 'input_fingerprint'), name='unique_completion_evaluation_input'
      ),
    ]


class Certificate(models.Model):
  completion = models.OneToOneField(
    CourseCompletion, on_delete=models.PROTECT, related_name='certificate',
    verbose_name='Finalización'
  )
  public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
  issued_at = models.DateTimeField(default=timezone.now)
  holder_name = models.CharField(max_length=300, verbose_name='Nombre en el certificado')
  course_title = models.CharField(max_length=150, verbose_name='Curso en el certificado')
  revoked_at = models.DateTimeField(null=True, blank=True)
  revocation_reason = models.CharField(max_length=500, blank=True, default='')

  @property
  def is_valid(self):
    return self.revoked_at is None

  class Meta:
    verbose_name = 'Certificado'
    verbose_name_plural = 'Certificados'
