import json

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import (
  OpenApiParameter,
  OpenApiResponse,
  extend_schema,
  extend_schema_view,
  inline_serializer,
)
from rest_framework import serializers
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

VALIDATION_ERROR = OpenApiResponse(
  description='Datos no válidos. El objeto contiene una lista de mensajes por campo.'
)
UNAUTHENTICATED = OpenApiResponse(description='No existe una sesión de Django válida.')
FORBIDDEN = OpenApiResponse(
  description='La sesión no tiene permiso o la validación CSRF ha fallado.'
)


def documented_viewset(resource, read_access, write_access):
  """Aplica descripciones uniformes de permisos, validación y CSRF al CRUD."""
  read_description = f'{resource}. Permiso de lectura: {read_access}'
  write_description = (
    f'{resource}. Permiso de escritura: {write_access} '
    'Requiere sesión y, en peticiones del navegador, cabecera X-CSRFToken.'
  )
  return extend_schema_view(
    list=extend_schema(description=read_description),
    retrieve=extend_schema(description=read_description),
    create=extend_schema(
      description=write_description,
      responses={201: None, 400: VALIDATION_ERROR, 401: UNAUTHENTICATED, 403: FORBIDDEN},
    ),
    update=extend_schema(
      description=write_description,
      responses={200: None, 400: VALIDATION_ERROR, 401: UNAUTHENTICATED, 403: FORBIDDEN},
    ),
    partial_update=extend_schema(
      description=write_description,
      responses={200: None, 400: VALIDATION_ERROR, 401: UNAUTHENTICATED, 403: FORBIDDEN},
    ),
    destroy=extend_schema(
      description=write_description,
      responses={204: None, 401: UNAUTHENTICATED, 403: FORBIDDEN},
    ),
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

  @extend_schema(
    request=RegisterSerializer,
    responses={201: UserSerializer, 400: VALIDATION_ERROR},
    description='Registro público. Valida los parámetros, incluida la confirmación de contraseña.',
    auth=[],
  )
  def post(self, request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
  permission_classes = (AllowAny,)
  authentication_classes = ()

  @extend_schema(
    request=inline_serializer(
      name='LoginRequest',
      fields={
        'username': serializers.CharField(),
        'password': serializers.CharField(write_only=True),
      },
    ),
    responses={200: UserSerializer, 400: VALIDATION_ERROR},
    description='Autentica credenciales y crea una sesión de Django en la cookie sessionid.',
    auth=[],
  )
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

  @extend_schema(
    request=None,
    responses={204: None, 401: UNAUTHENTICATED, 403: FORBIDDEN},
    description='Cierra la sesión. Requiere sesión y cabecera X-CSRFToken.',
  )
  def post(self, request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CurrentUserView(APIView):
  permission_classes = (IsAuthenticated,)

  @extend_schema(
    responses={200: UserSerializer, 401: UNAUTHENTICATED},
    description='Devuelve el usuario de la sesión y establece la cookie csrftoken.',
  )
  def get(self, request):
    return Response(UserSerializer(request.user).data)


@documented_viewset('Tipos de usuario', 'pública.', 'solo administración.')
class UserTypeViewSet(viewsets.ModelViewSet):
  queryset = UserType.objects.all()
  serializer_class = UserTypeSerializer
  permission_classes = (ReadOnlyOrAdmin,)


@documented_viewset('Perfiles', 'propietario o administración.', 'propietario o administración.')
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


@documented_viewset('Ofertas', 'pública.', 'solo administración.')
class OfferViewSet(viewsets.ModelViewSet):
  queryset = Offer.objects.all()
  serializer_class = OfferSerializer
  permission_classes = (ReadOnlyOrAdmin,)


@documented_viewset('Anuncios', 'pública.', 'empresa propietaria o administración.')
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


@documented_viewset(
  'Contenidos y archivos',
  'pública; los campos de archivo se devuelven como URL.',
  'solo administración; los archivos se envían como multipart/form-data.',
)
class ContentViewSet(viewsets.ModelViewSet):
  queryset = Content.objects.all()
  serializer_class = ContentSerializer
  permission_classes = (ReadOnlyOrAdmin,)


@documented_viewset('Cursos', 'pública.', 'profesor propietario o administración.')
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


@documented_viewset(
  'Matrículas',
  'alumno propietario, profesor del curso o administración.',
  'alumno propietario o administración.',
)
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


@documented_viewset(
  'Asistencias',
  'alumno implicado, profesor del curso o administración.',
  'profesor del curso o administración.',
)
class AttendanceViewSet(CourseRecordViewSet):
  queryset = Attendance.objects.select_related('course')
  serializer_class = AttendanceSerializer


@documented_viewset(
  'Notas',
  'alumno implicado, profesor del curso o administración.',
  'profesor del curso o administración.',
)
class MarkViewSet(CourseRecordViewSet):
  queryset = Mark.objects.select_related('course')
  serializer_class = MarkSerializer


@extend_schema_view(
  list=extend_schema(description='Lista los certificados del alumno de la sesión o todos para administración.'),
  retrieve=extend_schema(
    description='Consulta un certificado propio por su parámetro public_id UUID.',
    parameters=[OpenApiParameter('public_id', type={'type': 'string', 'format': 'uuid'}, location='path')],
  ),
  download=extend_schema(
    description='Descarga como archivo JSON un certificado propio identificado por public_id.',
    parameters=[OpenApiParameter('public_id', type={'type': 'string', 'format': 'uuid'}, location='path')],
    responses={(200, 'application/json'): CertificateSerializer, 401: UNAUTHENTICATED, 403: FORBIDDEN},
  ),
)
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

  @extend_schema(
    parameters=[OpenApiParameter('public_id', type={'type': 'string', 'format': 'uuid'}, location='path')],
    responses={200: CertificateSerializer, 404: OpenApiResponse(description='Certificado inexistente.')},
    description='Verificación pública mínima mediante el parámetro public_id UUID.',
    auth=[],
  )
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
