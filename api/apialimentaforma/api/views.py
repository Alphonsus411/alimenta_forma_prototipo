import json

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Announcement, Attendance, Certificate, Content, Course, Mark, Offer, Profile, Registration, UserType
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
  RegisterSerializer,
  UserSerializer,
  CertificateSerializer,
)


class RegisterView(APIView):
  permission_classes = (AllowAny,)
  authentication_classes = ()

  def post(self, request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
  permission_classes = (AllowAny,)
  authentication_classes = ()

  def post(self, request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    if not username or not password:
      return Response(
        {'non_field_errors': ['El nombre de usuario y la contraseña son obligatorios.']},
        status=status.HTTP_400_BAD_REQUEST,
      )
    user = authenticate(request, username=username, password=password)
    if user is None:
      return Response(
        {'non_field_errors': ['Las credenciales no son válidas.']},
        status=status.HTTP_400_BAD_REQUEST,
      )
    login(request, user)
    return Response(UserSerializer(user).data)


class LogoutView(APIView):
  permission_classes = (IsAuthenticated,)

  def post(self, request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CurrentUserView(APIView):
  permission_classes = (IsAuthenticated,)

  def get(self, request):
    return Response(UserSerializer(request.user).data)


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
    if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
      try:
        if self.request.user.profile.userType.category == 'p':
          return Registration.objects.filter(course__teacher=self.request.user)
      except (AttributeError, Profile.DoesNotExist, UserType.DoesNotExist):
        pass
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


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
  serializer_class = CertificateSerializer
  permission_classes = (IsAuthenticated,)
  lookup_field = 'public_id'

  def get_queryset(self):
    queryset = Certificate.objects.select_related(
      'completion__registration__student', 'completion__course'
    )
    if is_admin(self.request.user):
      return queryset
    return queryset.filter(completion__registration__student=self.request.user)

  @action(detail=True, methods=('get',))
  def download(self, request, public_id=None):
    certificate = self.get_object()
    payload = CertificateSerializer(certificate).data
    response = HttpResponse(
      json.dumps(payload, ensure_ascii=False, default=str, indent=2),
      content_type='application/json; charset=utf-8',
    )
    response['Content-Disposition'] = (
      f'attachment; filename="certificado-{certificate.public_id}.json"'
    )
    return response


class PublicCertificateVerificationView(APIView):
  permission_classes = (AllowAny,)
  authentication_classes = ()

  def get(self, request, public_id):
    certificate = Certificate.objects.select_related('completion').filter(
      public_id=public_id
    ).first()
    if certificate is None:
      return Response({'status': 'inexistente'}, status=status.HTTP_404_NOT_FOUND)
    return Response({
      'public_id': str(certificate.public_id),
      'status': 'vigente' if certificate.is_valid else 'revocado',
      'course_title': certificate.course_title,
      'issued_at': certificate.issued_at,
    })
