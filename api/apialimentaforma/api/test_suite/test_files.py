from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Announcement, UserType


class FileAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        company_role = UserType.objects.get_or_create(category='c')[0]
        cls.company = User.objects.create_user(username='file_company')
        cls.company.profile.userType = company_role
        cls.company.profile.save(update_fields=('userType',))

    @override_settings(MEDIA_ROOT='/tmp/alimenta-forma-test-media')
    def test_company_uploads_file_and_api_returns_its_url(self):
        self.client.force_authenticate(self.company)

        response = self.client.post(
            reverse('announcement-list'),
            {'detail': SimpleUploadedFile('vacante.txt', b'contenido')},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('vacante', response.data['detail'])
        announcement = Announcement.objects.get(pk=response.data['id'])
        self.addCleanup(lambda: Path(announcement.detail.path).unlink(missing_ok=True))
