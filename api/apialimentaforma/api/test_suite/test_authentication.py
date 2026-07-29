from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationAPITests(APITestCase):
    register_data = {
        'username': 'alumna',
        'email': 'alumna@example.com',
        'first_name': 'Ana',
        'last_name': 'López',
        'password': 'UnaClaveSegura_2026',
        'password_confirmation': 'UnaClaveSegura_2026',
        'category': 's',
    }

    def test_register_creates_user_with_hashed_password_and_category(self):
        response = self.client.post(reverse('auth-register'), self.register_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='alumna')
        self.assertTrue(user.check_password(self.register_data['password']))
        self.assertNotEqual(user.password, self.register_data['password'])
        self.assertEqual(user.profile.userType.category, 's')
        self.assertNotIn('password', response.data)

    def test_register_rejects_duplicate_username_and_email(self):
        self.client.post(reverse('auth-register'), self.register_data, format='json')
        duplicate = {**self.register_data, 'password': 'OtraClaveSegura_2026',
                     'password_confirmation': 'OtraClaveSegura_2026'}
        response = self.client.post(reverse('auth-register'), duplicate, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)

    def test_register_rejects_mismatched_and_invalid_passwords(self):
        mismatch = {**self.register_data, 'password_confirmation': 'NoCoincide_2026'}
        mismatch_response = self.client.post(reverse('auth-register'), mismatch, format='json')
        weak = {**self.register_data, 'password': '12345678', 'password_confirmation': '12345678'}
        weak_response = self.client.post(reverse('auth-register'), weak, format='json')

        self.assertIn('password_confirmation', mismatch_response.data)
        self.assertIn('password', weak_response.data)

    def test_register_rejects_disallowed_category(self):
        response = self.client.post(
            reverse('auth-register'), {**self.register_data, 'category': 'a'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)

    def test_login_rejects_wrong_credentials(self):
        User.objects.create_user(username='alumna', password='UnaClaveSegura_2026')
        response = self.client.post(
            reverse('auth-login'), {'username': 'alumna', 'password': 'incorrecta'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_login_authenticates_and_current_user_returns_identity(self):
        User.objects.create_user(username='alumna', email='alumna@example.com', password='UnaClaveSegura_2026')
        login_response = self.client.post(
            reverse('auth-login'), {'username': 'alumna', 'password': 'UnaClaveSegura_2026'}, format='json'
        )
        me_response = self.client.get(reverse('auth-current-user'))

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data['username'], 'alumna')

    def test_logout_ends_session(self):
        user = User.objects.create_user(username='alumna', password='UnaClaveSegura_2026')
        self.client.force_login(user)

        response = self.client.post(reverse('auth-logout'))
        me_response = self.client.get(reverse('auth-current-user'))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(me_response.status_code, status.HTTP_403_FORBIDDEN)
