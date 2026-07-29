"""Validadores y rutas seguras para los archivos subidos por usuarios."""

from pathlib import Path
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible


IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'webp')
IMAGE_CONTENT_TYPES = ('image/jpeg', 'image/png', 'image/webp')
CV_EXTENSIONS = ('pdf', 'doc', 'docx')
CV_CONTENT_TYPES = (
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
)
DOCUMENT_EXTENSIONS = ('pdf', 'doc', 'docx', 'odt', 'txt')
DOCUMENT_CONTENT_TYPES = CV_CONTENT_TYPES + (
  'application/vnd.oasis.opendocument.text',
  'text/plain',
)
VIDEO_EXTENSIONS = ('mp4', 'webm', 'ogv')
VIDEO_CONTENT_TYPES = ('video/mp4', 'video/webm', 'video/ogg')
ANNOUNCEMENT_EXTENSIONS = IMAGE_EXTENSIONS + ('pdf',)
ANNOUNCEMENT_CONTENT_TYPES = IMAGE_CONTENT_TYPES + ('application/pdf',)

MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_CV_SIZE = 5 * 1024 * 1024
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 50 * 1024 * 1024
MAX_ANNOUNCEMENT_SIZE = 10 * 1024 * 1024


@deconstructible
class FileSizeValidator:
  """Rechaza archivos cuyo tamaño supera el límite expresado en bytes."""

  def __init__(self, max_size):
    self.max_size = max_size

  def __call__(self, uploaded_file):
    if uploaded_file.size > self.max_size:
      limit_mb = self.max_size / (1024 * 1024)
      raise ValidationError(
        f'El archivo no puede superar {limit_mb:g} MB.',
        code='file_too_large',
      )


@deconstructible
class ContentTypeValidator:
  """Comprueba el tipo MIME declarado por el archivo subido."""

  def __init__(self, allowed_types):
    self.allowed_types = tuple(allowed_types)

  def __call__(self, uploaded_file):
    content_type = getattr(uploaded_file, 'content_type', None)
    if content_type not in self.allowed_types:
      raise ValidationError(
        'El tipo de archivo no está admitido.',
        code='invalid_content_type',
      )


def _validators(max_size, extensions, content_types):
  return [
    FileSizeValidator(max_size),
    FileExtensionValidator(allowed_extensions=extensions),
    ContentTypeValidator(content_types),
  ]


image_validators = _validators(MAX_IMAGE_SIZE, IMAGE_EXTENSIONS, IMAGE_CONTENT_TYPES)
cv_validators = _validators(MAX_CV_SIZE, CV_EXTENSIONS, CV_CONTENT_TYPES)
document_validators = _validators(
  MAX_DOCUMENT_SIZE, DOCUMENT_EXTENSIONS, DOCUMENT_CONTENT_TYPES
)
video_validators = _validators(MAX_VIDEO_SIZE, VIDEO_EXTENSIONS, VIDEO_CONTENT_TYPES)
announcement_validators = _validators(
  MAX_ANNOUNCEMENT_SIZE, ANNOUNCEMENT_EXTENSIONS, ANNOUNCEMENT_CONTENT_TYPES
)


def _safe_upload_path(directory, filename):
  """Genera una ruta normalizada sin reutilizar el nombre elegido por el cliente."""
  extension = Path(filename).suffix.lower()
  return f'uploads/{directory}/{uuid4().hex}{extension}'


def profile_image_upload_to(instance, filename):
  return _safe_upload_path('profiles/images', filename)


def profile_cv_upload_to(instance, filename):
  return _safe_upload_path('profiles/cv', filename)


def announcement_upload_to(instance, filename):
  return _safe_upload_path('announcements', filename)


def content_image_upload_to(instance, filename):
  return _safe_upload_path('content/images', filename)


def content_document_upload_to(instance, filename):
  return _safe_upload_path('content/documents', filename)


def content_video_upload_to(instance, filename):
  return _safe_upload_path('content/videos', filename)
