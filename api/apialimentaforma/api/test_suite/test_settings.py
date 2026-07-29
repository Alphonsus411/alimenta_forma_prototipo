from django.test import SimpleTestCase
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.settings import api_settings


class RestFrameworkSettingsTests(SimpleTestCase):
    def test_default_schema_class_resolves_to_openapi_auto_schema(self):
        self.assertIs(api_settings.DEFAULT_SCHEMA_CLASS, AutoSchema)
