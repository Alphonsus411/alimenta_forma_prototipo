from django.contrib.auth.models import User
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
