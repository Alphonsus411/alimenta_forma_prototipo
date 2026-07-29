from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from .models import UserType, Profile, Offer, Announcement, Content, Course, Registration, Attendance, Mark

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

class CourseSerializer (serializers.ModelSerializer):
  class Meta:
    model = Course
    fields = '__all__'
    read_only_fields = ('teacher',)

class RegistrationSerializer (serializers.ModelSerializer):
  class Meta:
    model = Registration
    fields = '__all__'
    read_only_fields = ('student',)

class AttendanceSerializer (serializers.ModelSerializer):
  class Meta:
    model = Attendance
    fields = '__all__'

class MarkSerializer (serializers.ModelSerializer):
  # El rol se modela mediante Profile/UserType, no mediante grupos de Django.
  student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

  class Meta:
    model = Mark
    fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
  category = serializers.CharField(source='profile.userType.category', read_only=True)

  class Meta:
    model = User
    fields = ('id', 'username', 'email', 'first_name', 'last_name', 'category')


class RegisterSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, trim_whitespace=False)
  password_confirmation = serializers.CharField(write_only=True, trim_whitespace=False)
  category = serializers.ChoiceField(choices=('s', 'p', 'c'), write_only=True)

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
