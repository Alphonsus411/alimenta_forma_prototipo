from django.test import TestCase
from django.urls import reverse
from drf_spectacular.validation import validate_schema


class OpenApiSchemaTests(TestCase):
  def test_schema_es_valido_y_publica_endpoints_principales(self):
    response = self.client.get(reverse('api-schema'), HTTP_ACCEPT='application/json')

    self.assertEqual(response.status_code, 200)
    schema = response.json()
    validate_schema(schema)

    self.assertEqual(schema['openapi'], '3.0.3')
    expected_paths = {
      '/api/v1/auth/register/',
      '/api/v1/auth/login/',
      '/api/v1/auth/logout/',
      '/api/v1/auth/me/',
      '/api/v1/profile/',
      '/api/v1/course/',
      '/api/v1/registration/',
      '/api/v1/attendance/',
      '/api/v1/mark/',
      '/api/v1/content/',
      '/api/v1/certificates/',
      '/api/v1/certificates/verify/{public_id}/',
    }
    self.assertTrue(expected_paths.issubset(schema['paths']))
    self.assertIn('cookieAuth', schema['components']['securitySchemes'])

  def test_documentacion_interactiva_usa_el_esquema_estable(self):
    response = self.client.get(reverse('api-docs'))

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, reverse('api-schema'))
