from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .roles import PUBLIC_REGISTRATION_ROLES
from .permissions import is_admin
from .models import Certificate, UserType, Profile, Offer, Announcement, Content, Course, CourseLesson, Registration, Attendance, Mark
from .services.attendance import AttendanceDomainError, validate_attendance_context

class UserTypeSerializer (serializers.ModelSerializer):
  class Meta:
    model = UserType
    fields = '__all__'

class ProfileSerializer (serializers.ModelSerializer):
  class Meta:
    model = Profile
    fields = '__all__'
    read_only_fields = ('user',)

class OfferSerializer (serializers.ModelSerializer):
  class Meta:
    model = Offer
    fields = '__all__'

class AnnouncementSerializer (serializers.ModelSerializer):
  class Meta:
    model = Announcement
    fields = '__all__'
    read_only_fields = ('owner',)

class ContentSerializer (serializers.ModelSerializer):
  class Meta:
    model = Content
    fields = '__all__'

class CourseLessonSerializer(serializers.ModelSerializer):
  title = serializers.CharField(source='content.title', read_only=True)
  comment = serializers.CharField(source='content.comment', read_only=True)

  class Meta:
    model = CourseLesson
    fields = ('id', 'content', 'order', 'title', 'comment')


class CourseSerializer(serializers.ModelSerializer):
  lessons = CourseLessonSerializer(many=True, read_only=True)
  teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
  category_name = serializers.CharField(source='category.name', read_only=True)
  modality_display = serializers.CharField(source='get_modality_display', read_only=True)
  status_display = serializers.CharField(source='get_status_display', read_only=True)

  def validate(self, attrs):
    requested_status = attrs.get('status')
    if requested_status in (Course.Status.PUBLISHED, Course.Status.CANCELLED, Course.Status.CLOSED):
      request = self.context.get('request')
      if not request or not is_admin(request.user):
        raise serializers.ValidationError({
          'status': 'Solo administración puede publicar, cancelar o cerrar cursos.'
        })
    request = self.context.get('request')
    if not self.instance and not request:
      return attrs
    instance = self.instance or Course(teacher=request.user)
    for field, value in attrs.items():
      setattr(instance, field, value)
    try:
      instance.clean()
    except DjangoValidationError as error:
      raise serializers.ValidationError(error.message_dict) from error
    return attrs

  class Meta:
    model = Course
    fields = '__all__'
    read_only_fields = ('teacher',)
    extra_kwargs = {
      field: {'required': True}
      for field in (
        'category', 'modality', 'duration_hours', 'start_date', 'end_date',
        'capacity', 'location', 'price', 'objectives', 'requirements',
      )
    }

class RegistrationSerializer (serializers.ModelSerializer):
  student_username = serializers.CharField(source='student.username', read_only=True)
  def validate(self, attrs):
    request = self.context.get('request')
    student = request.user if request and request.user.is_authenticated else None
    course = attrs.get('course', getattr(self.instance, 'course', None))
    if (
      student and course and
      Registration.objects.exclude(pk=getattr(self.instance, 'pk', None)).filter(
        course=course, student=student
      ).exists()
    ):
      raise serializers.ValidationError({
        'course': 'Ya existe una matrícula de este estudiante para el curso.'
      })
    return attrs

  class Meta:
    model = Registration
    fields = '__all__'
    read_only_fields = ('student',)

class AttendanceSerializer (serializers.ModelSerializer):
  student_username = serializers.CharField(source='student.username', read_only=True)
  def validate(self, attrs):
    course = attrs.get('course', getattr(self.instance, 'course', None))
    student = attrs.get('student', getattr(self.instance, 'student', None))
    try:
      validate_attendance_context(course.id, student.id)
    except AttendanceDomainError as error:
      raise serializers.ValidationError(str(error)) from error
    return attrs

  class Meta:
    model = Attendance
    fields = '__all__'

class MarkSerializer (serializers.ModelSerializer):
  # El rol se modela mediante Profile/UserType, no mediante grupos de Django.
  student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

  def validate(self, attrs):
    course = attrs.get('course', getattr(self.instance, 'course', None))
    student = attrs.get('student', getattr(self.instance, 'student', None))
    if course and student and not Registration.objects.filter(course=course, student=student).exists():
      raise serializers.ValidationError({
        'student': 'No existe una matrícula del alumno para este curso.'
      })
    return attrs

  class Meta:
    model = Mark
    fields = '__all__'


class CertificateSerializer(serializers.ModelSerializer):
  status = serializers.SerializerMethodField()
  outcome = serializers.CharField(source='completion.outcome', read_only=True)

  def get_status(self, obj):
    return 'vigente' if obj.is_valid else 'revocado'

  class Meta:
    model = Certificate
    fields = (
      'public_id', 'issued_at', 'holder_name', 'course_title', 'status', 'outcome',
    )


class UserSerializer(serializers.ModelSerializer):
  category = serializers.CharField(source='profile.userType.category', read_only=True)

  class Meta:
    model = User
    fields = ('id', 'username', 'email', 'first_name', 'last_name', 'category')


class RegisterSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, trim_whitespace=False)
  password_confirmation = serializers.CharField(write_only=True, trim_whitespace=False)
  category = serializers.ChoiceField(choices=PUBLIC_REGISTRATION_ROLES, write_only=True)

  class Meta:
    model = User
    fields = (
      'username', 'email', 'first_name', 'last_name', 'password',
      'password_confirmation', 'category',
    )
    extra_kwargs = {
      'email': {'required': True, 'allow_blank': False},
      'first_name': {'required': True, 'allow_blank': False},
      'last_name': {'required': True, 'allow_blank': False},
    }

  def validate_email(self, value):
    if User.objects.filter(email__iexact=value).exists():
      raise serializers.ValidationError('Ya existe un usuario con este correo electrónico.')
    return value.lower()

  def validate(self, attrs):
    if attrs['password'] != attrs['password_confirmation']:
      raise serializers.ValidationError({
        'password_confirmation': 'Las contraseñas no coinciden.',
      })
    candidate = User(
      username=attrs.get('username'), email=attrs.get('email'),
      first_name=attrs.get('first_name'), last_name=attrs.get('last_name'),
    )
    try:
      validate_password(attrs['password'], candidate)
    except DjangoValidationError as error:
      raise serializers.ValidationError({'password': list(error.messages)}) from error
    return attrs

  @transaction.atomic
  def create(self, validated_data):
    category = validated_data.pop('category')
    validated_data.pop('password_confirmation')
    password = validated_data.pop('password')
    user = User.objects.create_user(password=password, **validated_data)
    user_type, _ = UserType.objects.get_or_create(category=category)
    user.profile.userType = user_type
    user.profile.save(update_fields=('userType',))
    return user
