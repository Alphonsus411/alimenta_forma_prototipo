import shutil
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Announcement, UserType
from api.validators import (
    MAX_ANNOUNCEMENT_SIZE,
    MAX_CV_SIZE,
    MAX_DOCUMENT_SIZE,
    MAX_IMAGE_SIZE,
    MAX_VIDEO_SIZE,
    announcement_validators,
    cv_validators,
    document_validators,
    image_validators,
    video_validators,
)


class ReusableFileValidatorTests(SimpleTestCase):
    file_kinds = (
        ('imagen', image_validators, MAX_IMAGE_SIZE, 'foto.png', 'image/png'),
        ('CV', cv_validators, MAX_CV_SIZE, 'curriculum.pdf', 'application/pdf'),
        (
            'documento', document_validators, MAX_DOCUMENT_SIZE,
            'apuntes.txt', 'text/plain',
        ),
        ('vídeo', video_validators, MAX_VIDEO_SIZE, 'clase.mp4', 'video/mp4'),
        (
            'anuncio', announcement_validators, MAX_ANNOUNCEMENT_SIZE,
            'oferta.pdf', 'application/pdf',
        ),
    )

    def assert_validators_accept(self, validators, uploaded_file):
        for validator in validators:
            validator(uploaded_file)

    def assert_validators_reject(self, validators, uploaded_file):
        with self.assertRaises(ValidationError):
            for validator in validators:
                validator(uploaded_file)

    def test_valid_files_are_accepted(self):
        for kind, validators, _limit, filename, content_type in self.file_kinds:
            with self.subTest(kind=kind):
                uploaded_file = SimpleUploadedFile(
                    filename, b'contenido valido', content_type=content_type
                )
                self.assert_validators_accept(validators, uploaded_file)

    def test_files_larger_than_each_limit_are_rejected(self):
        for kind, validators, limit, filename, content_type in self.file_kinds:
            with self.subTest(kind=kind):
                uploaded_file = SimpleUploadedFile(filename, b'x', content_type=content_type)
                uploaded_file.size = limit + 1
                self.assert_validators_reject(validators, uploaded_file)

    def test_disallowed_content_types_are_rejected(self):
        for kind, validators, _limit, filename, _content_type in self.file_kinds:
            with self.subTest(kind=kind):
                uploaded_file = SimpleUploadedFile(
                    filename, b'contenido', content_type='application/x-msdownload'
                )
                self.assert_validators_reject(validators, uploaded_file)

    def test_disallowed_extensions_are_rejected(self):
        for kind, validators, _limit, _filename, content_type in self.file_kinds:
            with self.subTest(kind=kind):
                uploaded_file = SimpleUploadedFile(
                    'archivo.exe', b'contenido', content_type=content_type
                )
                self.assert_validators_reject(validators, uploaded_file)


class FileAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        company_role = UserType.objects.get_or_create(category='c')[0]
        cls.company = User.objects.create_user(username='file_company')
        cls.company.profile.userType = company_role
        cls.company.profile.save(update_fields=('userType',))

    def test_company_uploads_file_and_api_returns_its_url(self):
        media_root = tempfile.mkdtemp(prefix='alimenta-forma-test-media-')
        self.addCleanup(shutil.rmtree, media_root, True)
        self.client.force_authenticate(self.company)

        with override_settings(MEDIA_ROOT=media_root):
            response = self.client.post(
                reverse('announcement-list'),
                {'detail': SimpleUploadedFile(
                    'vacante.pdf', b'%PDF-1.4 contenido', content_type='application/pdf'
                )},
                format='multipart',
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        announcement = Announcement.objects.get(pk=response.data['id'])
        uploaded_path = Path(announcement.detail.name)
        self.assertEqual(uploaded_path.parent.as_posix(), 'uploads/announcements')
        self.assertEqual(uploaded_path.suffix, '.pdf')
        self.assertNotIn('vacante', uploaded_path.name)

    def test_api_rejects_an_unsupported_announcement_type(self):
        self.client.force_authenticate(self.company)

        response = self.client.post(
            reverse('announcement-list'),
            {'detail': SimpleUploadedFile(
                'programa.exe', b'contenido', content_type='application/x-msdownload'
            )},
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
