from django.db import connection
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from api.views import LoginView
from rest_framework import status


class LoginViewTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = LoginView.as_view()
        with connection.cursor() as cursor:
            cursor.execute(
                'CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(150) NOT NULL UNIQUE, password VARCHAR(128) NOT NULL);')
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (%s, %s)',
                ['testuser', 'testpassword'])

    def test_valid_credentials(self):
        request = self.factory.post(
            '/login/', {'username': 'testuser', 'password': 'testpassword'})
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_missing_credentials(self):
        request = self.factory.post('/login/', {'username': 'testuser'})
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['error'],
            'Username and password are required')

    def test_invalid_credentials(self):
        request = self.factory.post(
            '/login/', {'username': 'testuser', 'password': 'invalidpassword'})
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Invalid Credentials')
