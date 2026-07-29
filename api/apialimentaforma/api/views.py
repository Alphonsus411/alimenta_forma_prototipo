from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Announcement, Attendance, Content, Course, Mark, Offer, Profile, Registration, UserType
from .permissions import (
  IsAuthenticatedProfileOwnerOrAdmin,
  IsCompanyAnnouncementOwnerOrAdmin,
  IsRegistrationOwnerOrAdmin,
  IsTeacherCourseOwnerOrAdmin,
  IsTeacherOfCourseOrStudentOrAdmin,
  ReadOnlyOrAdmin,
  is_admin,
)
from .serializer import (
  AnnouncementSerializer,
  AttendanceSerializer,
  ContentSerializer,
  CourseSerializer,
  MarkSerializer,
  OfferSerializer,
  ProfileSerializer,
  RegistrationSerializer,
  UserTypeSerializer,
)


class UserTypeViewSet(viewsets.ModelViewSet):
  queryset = UserType.objects.all()
  serializer_class = UserTypeSerializer
  permission_classes = (ReadOnlyOrAdmin,)


class ProfileViewSet(viewsets.ModelViewSet):
  queryset = Profile.objects.all()
  serializer_class = ProfileSerializer
  permission_classes = (IsAuthenticatedProfileOwnerOrAdmin,)

  def get_queryset(self):
    if is_admin(self.request.user):
      return Profile.objects.all()
    return Profile.objects.filter(user=self.request.user)

  def perform_create(self, serializer):
    serializer.save(user=self.request.user)


class OfferViewSet(viewsets.ModelViewSet):
  queryset = Offer.objects.all()
  serializer_class = OfferSerializer
  permission_classes = (ReadOnlyOrAdmin,)


class AnnouncementViewSet(viewsets.ModelViewSet):
  queryset = Announcement.objects.all()
  serializer_class = AnnouncementSerializer
  permission_classes = (IsCompanyAnnouncementOwnerOrAdmin,)

  def get_queryset(self):
    queryset = Announcement.objects.all()
    if self.request.method not in ('GET', 'HEAD', 'OPTIONS') and not is_admin(self.request.user):
      return queryset.filter(owner=self.request.user)
    return queryset

  def perform_create(self, serializer):
    serializer.save(owner=self.request.user)


class ContentViewSet(viewsets.ModelViewSet):
  queryset = Content.objects.all()
  serializer_class = ContentSerializer
  permission_classes = (ReadOnlyOrAdmin,)


class CourseViewSet(viewsets.ModelViewSet):
  queryset = Course.objects.all()
  serializer_class = CourseSerializer
  permission_classes = (IsTeacherCourseOwnerOrAdmin,)

  def get_queryset(self):
    queryset = Course.objects.all()
    if self.request.method not in ('GET', 'HEAD', 'OPTIONS') and not is_admin(self.request.user):
      return queryset.filter(teacher=self.request.user)
    return queryset

  def perform_create(self, serializer):
    serializer.save(teacher=self.request.user)


class RegistrationViewSet(viewsets.ModelViewSet):
  queryset = Registration.objects.all()
  serializer_class = RegistrationSerializer
  permission_classes = (IsRegistrationOwnerOrAdmin,)

  def get_queryset(self):
    if is_admin(self.request.user):
      return Registration.objects.all()
    return Registration.objects.filter(student=self.request.user)

  def perform_create(self, serializer):
    serializer.save(student=self.request.user)


class CourseRecordViewSet(viewsets.ModelViewSet):
  permission_classes = (IsTeacherOfCourseOrStudentOrAdmin,)

  def get_queryset(self):
    queryset = self.queryset
    if is_admin(self.request.user):
      return queryset
    return queryset.filter(course__teacher=self.request.user) | queryset.filter(student=self.request.user)

  def _check_course_teacher(self, course):
    if not is_admin(self.request.user) and course.teacher_id != self.request.user.id:
      raise PermissionDenied('Solo el profesor del curso puede gestionar este registro.')

  def perform_create(self, serializer):
    self._check_course_teacher(serializer.validated_data['course'])
    serializer.save()

  def perform_update(self, serializer):
    self._check_course_teacher(serializer.validated_data.get('course', serializer.instance.course))
    serializer.save()


class AttendanceViewSet(CourseRecordViewSet):
  queryset = Attendance.objects.select_related('course')
  serializer_class = AttendanceSerializer


class MarkViewSet(CourseRecordViewSet):
  queryset = Mark.objects.select_related('course')
  serializer_class = MarkSerializer
