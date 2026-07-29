from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save
from django.utils import timezone


def validate_user_role(user, expected_role, field_name):
  """Valida el rol de dominio almacenado en el perfil de un usuario."""
  try:
    role = user.profile.userType.category
  except (Profile.DoesNotExist, UserType.DoesNotExist):
    role = None
  if role != expected_role:
    role_name = 'profesor' if expected_role == 'p' else 'estudiante'
    raise ValidationError({field_name: f'El usuario debe tener el rol {role_name}.'})

# TIPOS DE USUARIO ---------------------------------------------

class UserType (models.Model):
  categoryChoices = (
    ('c', 'empresa'),
    ('p', 'profesor'),
    ('s', 'estudiante'),
    ('a', 'administrador')
  )
  category = models.CharField(max_length=1, choices= categoryChoices, default= 's', verbose_name= 'Categoria')

  def __str__(self):
    return self.category
  
  class Meta:
    verbose_name= 'Categoria'
    verbose_name_plural= 'Categorias'

# PERFIL DE CADA USUARIO -----------------------------------------

class Profile (models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name= 'profile', verbose_name= 'Usuario')
  location = models.CharField(max_length=150, blank=True, default='', verbose_name= 'Ciudad')
  image = models.ImageField(default='defaultUser.png', upload_to='user/', verbose_name= 'Imagen')
  phone = models.CharField(max_length= 15, blank=True, default='', verbose_name= 'Telefono')
  description = models.CharField(max_length= 500, blank=True, default='', verbose_name= 'Descripcion')
  userType = models.ForeignKey(UserType, on_delete= models.CASCADE, verbose_name= 'Categoria')
  cv = models.FileField(upload_to='user/',blank= True, null=True, verbose_name= 'CV')

  def __str__(self):
    return self.user.username

  class Meta:
    verbose_name = 'perfil'
    verbose_name_plural = 'perfiles'
    ordering = ['-id']

def create_user_profile (sender, instance, created, **kwargs):
    if created:
        default_user_type, _ = UserType.objects.get_or_create(category='s')
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
  detail =  models.FileField(upload_to='Announcement/', verbose_name = 'Detalle')
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
  img = models.ImageField(upload_to='material/', blank= True, null= True , verbose_name= 'Material grafico')
  doc = models.FileField(upload_to='material/', blank= True, null= True , verbose_name= 'Material escrito')
  videos = models.FileField(upload_to='material/', blank= True, null= True , verbose_name= 'Material de video')

  def __str__(self):
    return self.title

  class Meta:
    verbose_name = 'Contenido'
    verbose_name_plural = 'Contenidos'

# CURSOS DISPONIBLES, LOS COLOCAN LOS PROFESORES ---------------------------------------------

class Course (models.Model):
  statusChoices = (
    ('i', 'inscripción'),
    ('d', 'desarrollo'),
    ('f', 'finalizado'),
  )

  title = models.CharField(max_length=150, verbose_name= 'Titulo')
  detail = models.CharField(max_length=500, verbose_name = 'Detalle')
  classes = models.IntegerField(validators=[MinValueValidator(1)], verbose_name= 'Clases')
  teacher = models.ForeignKey(User, verbose_name= 'Profesor', on_delete=models.CASCADE)
  status = models.CharField(max_length=1, choices= statusChoices, default= 'i', verbose_name= 'Estado')
  content = models.ForeignKey(Content, on_delete=models.CASCADE, blank= True, null=True, verbose_name='Contenido')

  def __str__(self):
    return self.title

  def clean(self):
    super().clean()
    validate_user_role(self.teacher, 'p', 'teacher')
  
  class Meta:
    verbose_name = 'Curso'
    verbose_name_plural = 'Cursos'
    constraints = [
      models.CheckConstraint(check=models.Q(classes__gt=0), name='course_classes_positive'),
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
    validate_user_role(self.student, 's', 'student')
  
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
    validate_user_role(self.student, 's', 'student')

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
  student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'estudiantes'}, verbose_name='Estudiante')
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
    validate_user_role(self.student, 's', 'student')
  
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
