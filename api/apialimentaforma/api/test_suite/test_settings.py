import json
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.settings import api_settings

from apialimentaforma.environment import env_bool, env_int, env_json, env_list


class RestFrameworkSettingsTests(SimpleTestCase):
    def test_default_schema_class_resolves_to_openapi_auto_schema(self):
        self.assertIs(api_settings.DEFAULT_SCHEMA_CLASS, AutoSchema)


class EnvironmentParserTests(SimpleTestCase):
    def test_parses_typed_values(self):
        values = {
            'TEST_BOOLEAN': 'yes',
            'TEST_INTEGER': '30',
            'TEST_LIST': 'uno, dos,,tres',
            'TEST_JSON': '{"sslmode": "require"}',
        }
        with mock.patch.dict(os.environ, values):
            self.assertTrue(env_bool('TEST_BOOLEAN'))
            self.assertEqual(env_int('TEST_INTEGER', 0), 30)
            self.assertEqual(env_list('TEST_LIST'), ['uno', 'dos', 'tres'])
            self.assertEqual(env_json('TEST_JSON'), {'sslmode': 'require'})

    def test_rejects_invalid_typed_values(self):
        with mock.patch.dict(os.environ, {'TEST_BOOLEAN': 'quizá'}):
            with self.assertRaisesMessage(ImproperlyConfigured, 'TEST_BOOLEAN'):
                env_bool('TEST_BOOLEAN')
        with mock.patch.dict(os.environ, {'TEST_JSON': '[]'}):
            with self.assertRaisesMessage(ImproperlyConfigured, 'objeto JSON'):
                env_json('TEST_JSON')


class ProductionSettingsTests(SimpleTestCase):
    project_dir = Path(__file__).resolve().parents[2]

    def run_settings_import(self, code='import apialimentaforma.settings', **overrides):
        environment = os.environ.copy()
        environment.update(
            {
                'APP_ENV': 'production',
                'SECRET_KEY': '',
                'DEBUG': 'false',
                'ALLOWED_HOSTS': 'example.com',
                'DB_NAME': '/tmp/alimenta-forma-settings-test.sqlite3',
            }
        )
        environment.update(overrides)
        return subprocess.run(
            [sys.executable, '-c', code],
            cwd=self.project_dir,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_production_requires_secret_key(self):
        result = self.run_settings_import()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('SECRET_KEY', result.stderr)

    def test_valid_production_configuration_loads(self):
        result = self.run_settings_import(SECRET_KEY='s' * 50)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_rejects_debug(self):
        result = self.run_settings_import(SECRET_KEY='s' * 50, DEBUG='true')

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DEBUG no puede estar activo', result.stderr)

    def test_production_enables_https_protection_and_optional_proxy_header(self):
        code = (
            'import json; import apialimentaforma.settings as s; '
            'print(json.dumps({'
            '"session": s.SESSION_COOKIE_SECURE, '
            '"csrf": s.CSRF_COOKIE_SECURE, '
            '"redirect": s.SECURE_SSL_REDIRECT, '
            '"hsts": s.SECURE_HSTS_SECONDS, '
            '"proxy": s.SECURE_PROXY_SSL_HEADER}))'
        )
        result = self.run_settings_import(
            code,
            SECRET_KEY='s' * 50,
            TRUST_X_FORWARDED_PROTO='true',
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        values = json.loads(result.stdout)
        self.assertTrue(values['session'])
        self.assertTrue(values['csrf'])
        self.assertTrue(values['redirect'])
        self.assertEqual(values['hsts'], 31536000)
        self.assertEqual(values['proxy'], ['HTTP_X_FORWARDED_PROTO', 'https'])
