from django.db import connection
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status

from authentication.views import LoginView


class LoginViewTestCase(TestCase):

    def setUp(self):
        """
        Initialize the test case by creating a table and inserting a user
        in the database.
        """
        self.factory = APIRequestFactory()
        self.view = LoginView.as_view()

        # Raw SQL for table creation and user insertion
        with connection.cursor() as cursor:
            # Create the 'users' table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(150) NOT NULL UNIQUE,
                    password VARCHAR(128) NOT NULL
                );
            ''')

            # Insert a user into the 'users' table
            cursor.execute('''
                INSERT INTO users (username, password) VALUES (%s, %s)
            ''', ['testuser', 'testpassword'])

    def test_valid_credentials(self):
        """
        Test the LoginView with valid credentials.

        This test case sends a POST request to the '/login/' endpoint with
        valid credentials ('testuser' and 'testpassword'). It then checks if
        the response status code is 200 OK and if the response data contains
        the user's username, a refresh token, and an access token.
        """
        # Create a POST request with valid credentials
        request = self.factory.post(
            '/login/', {'username': 'testuser', 'password': 'testpassword'})

        # Send the request to the LoginView
        response = self.view(request)

        # Check if the response status code is 200 OK
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Expected status code 200, received %s" %
            response.status_code)

        # Check if the response data contains the user's username
        self.assertEqual(
            response.data['user']['username'], 'testuser',
            "Expected username 'testuser', received %s" %
            response.data['user']['username'])

        # Check if the response data contains a refresh token
        self.assertIn(
            'refresh', response.data,
            "Expected refresh token not found in response data")

        # Check if the response data contains an access token
        self.assertIn(
            'access', response.data,
            "Expected access token not found in response data")

    def test_missing_credentials(self):
        """
        Test the LoginView with missing credentials.

        This test case sends a POST request to the '/login/' endpoint with
        missing credentials ('testuser' and no password). It then checks if
        the response status code is 400 Bad Request and if the response data
        contains an error message indicating that the username and password
        are required.
        """
        # Create a POST request with missing credentials
        request = self.factory.post('/login/', {'username': 'testuser'})

        # Send the request to the LoginView
        response = self.view(request)

        # Check if the response status code is 400 Bad Request
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "Expected status code 400, received %s" %
            response.status_code)

        # Check if the response data contains an error message
        self.assertEqual(
            response.data['error'],
            'Username and password are required',
            "Expected error message 'Username and password are required', "
            "received %s" % response.data['error'])

    def test_invalid_credentials(self):
        """
        Test the LoginView with invalid credentials.

        This test case sends a POST request to the '/login/' endpoint with
        invalid credentials ('testuser' and 'invalidpassword'). It then checks if
        the response status code is 401 Unauthorized and if the response data
        contains an error message indicating that the credentials are invalid.
        """
        # Create a POST request with invalid credentials
        request = self.factory.post(
            '/login/', {'username': 'testuser', 'password': 'invalidpassword'})

        # Send the request to the LoginView
        response = self.view(request)

        # Check if the response status code is 401 Unauthorized
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Expected status code 401, received %s" % response.status_code)

        # Check if the response data contains an error message
        self.assertEqual(
            response.data['error'], 'Invalid Credentials',
            "Expected error message 'Invalid Credentials', received %s" %
            response.data['error'])
