from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.models import Announcement, Attendance, Course, Mark, Registration, UserType


class DomainPermissionTests(APITestCase):
  @classmethod
  def setUpTestData(cls):
    cls.roles = {
      role: UserType.objects.get_or_create(category=role)[0]
      for role in ('a', 'c', 'p', 's')
    }
    cls.admin = cls.make_user('admin', 'a', is_staff=True)
    cls.company = cls.make_user('empresa', 'c')
    cls.other_company = cls.make_user('otra_empresa', 'c')
    cls.teacher = cls.make_user('profesor', 'p')
    cls.other_teacher = cls.make_user('otro_profesor', 'p')
    cls.student = cls.make_user('estudiante', 's')
    cls.other_student = cls.make_user('otro_estudiante', 's')
    cls.course = Course.objects.create(title='Curso', detail='Detalle', classes=3, teacher=cls.teacher)
    cls.other_course = Course.objects.create(title='Ajeno', detail='Detalle', classes=3, teacher=cls.other_teacher)
    cls.registration = Registration.objects.create(course=cls.course, student=cls.student)
    cls.other_registration = Registration.objects.create(course=cls.course, student=cls.other_student)
    cls.attendance = Attendance.objects.create(course=cls.course, student=cls.student, present=True)
    cls.mark = Mark.objects.create(course=cls.course, student=cls.student, mark_1=8)
    cls.announcement = Announcement.objects.create(
      owner=cls.company,
      detail=SimpleUploadedFile(
        'anuncio.pdf', b'%PDF-1.4 anuncio', content_type='application/pdf'
      ),
    )

  @classmethod
  def make_user(cls, username, role, **kwargs):
    user = User.objects.create_user(username=username, password='password', **kwargs)
    user.profile.userType = cls.roles[role]
    user.profile.save()
    return user

  def setUp(self):
    self.client = APIClient()

  def login(self, user):
    self.client.force_authenticate(user)

  def test_anonymous_can_read_public_catalogue_but_cannot_write(self):
    self.assertEqual(self.client.get(reverse('course-list')).status_code, status.HTTP_200_OK)
    response = self.client.post(
      reverse('course-list'),
      {'title': 'Nuevo', 'detail': 'Detalle', 'classes': 2},
    )
    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    self.assertEqual(self.client.get(reverse('profile-list')).status_code, status.HTTP_403_FORBIDDEN)
    self.assertEqual(self.client.get(reverse('mark-list')).status_code, status.HTTP_403_FORBIDDEN)

  def test_profile_is_visible_only_to_owner_and_admin(self):
    self.login(self.student)
    response = self.client.get(reverse('profile-list'))
    self.assertEqual([item['user'] for item in response.data], [self.student.id])
    self.assertEqual(
      self.client.get(reverse('profile-detail', args=[self.other_student.profile.id])).status_code,
      status.HTTP_404_NOT_FOUND,
    )
    self.login(self.admin)
    self.assertGreater(len(self.client.get(reverse('profile-list')).data), 1)

  def test_registration_owner_is_derived_and_foreign_objects_are_hidden(self):
    self.login(self.student)
    response = self.client.post(
      reverse('registration-list'),
      {'course': self.other_course.id, 'student': self.other_student.id},
    )
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data['student'], self.student.id)
    self.assertEqual(
      self.client.get(reverse('registration-detail', args=[self.other_registration.id])).status_code,
      status.HTTP_404_NOT_FOUND,
    )
    self.login(self.company)
    self.assertEqual(
      self.client.post(reverse('registration-list'), {'course': self.course.id}).status_code,
      status.HTTP_403_FORBIDDEN,
    )

  def test_only_company_creates_announcement_and_owner_is_derived(self):
    self.login(self.student)
    self.assertEqual(
      self.client.post(reverse('announcement-list'), {'detail': SimpleUploadedFile('x.txt', b'x')}).status_code,
      status.HTTP_403_FORBIDDEN,
    )
    self.login(self.company)
    response = self.client.post(
      reverse('announcement-list'),
      {
        'detail': SimpleUploadedFile(
          'nuevo.pdf', b'%PDF-1.4 nuevo', content_type='application/pdf'
        ),
        'owner': self.other_company.id,
      },
      format='multipart',
    )
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data['owner'], self.company.id)
    self.login(self.other_company)
    self.assertEqual(
      self.client.delete(reverse('announcement-detail', args=[self.announcement.id])).status_code,
      status.HTTP_404_NOT_FOUND,
    )

  def test_only_course_teacher_can_write_marks_and_attendance(self):
    payload = {'course': self.course.id, 'student': self.other_student.id, 'mark_1': 7}
    self.login(self.other_teacher)
    self.assertEqual(self.client.post(reverse('mark-list'), payload).status_code, status.HTTP_403_FORBIDDEN)
    self.login(self.teacher)
    self.assertEqual(self.client.post(reverse('mark-list'), payload).status_code, status.HTTP_201_CREATED)
    attendance_payload = {'course': self.course.id, 'student': self.other_student.id, 'present': False}
    self.assertEqual(
      self.client.post(reverse('attendance-list'), attendance_payload).status_code,
      status.HTTP_201_CREATED,
    )

  def test_student_reads_own_records_but_cannot_change_them(self):
    self.login(self.student)
    self.assertEqual(len(self.client.get(reverse('mark-list')).data), 1)
    self.assertEqual(len(self.client.get(reverse('attendance-list')).data), 1)
    self.assertEqual(
      self.client.patch(reverse('mark-detail', args=[self.mark.id]), {'mark_1': 10}).status_code,
      status.HTTP_403_FORBIDDEN,
    )

  def test_teacher_cannot_modify_another_teachers_course(self):
    self.login(self.teacher)
    self.assertEqual(
      self.client.patch(reverse('course-detail', args=[self.other_course.id]), {'title': 'Intruso'}).status_code,
      status.HTTP_404_NOT_FOUND,
    )
    response = self.client.post(
      reverse('course-list'),
      {'title': 'Propio', 'detail': 'Detalle', 'classes': 2, 'teacher': self.other_teacher.id},
    )
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data['teacher'], self.teacher.id)

  def test_admin_can_manage_foreign_objects(self):
    self.login(self.admin)
    self.assertEqual(
      self.client.patch(reverse('mark-detail', args=[self.mark.id]), {'mark_1': 9}).status_code,
      status.HTTP_200_OK,
    )
    self.assertEqual(
      self.client.delete(reverse('registration-detail', args=[self.other_registration.id])).status_code,
      status.HTTP_204_NO_CONTENT,
    )
