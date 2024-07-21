from django.db import connection
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework import status

from api.models import User
from api.views import LoginView, BookListView


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


class BookListViewTestCase(TestCase):

    def setUp(self):
        """
        Set up the test case by creating the 'books' table and inserting
        sample books with the specified conditions.
        """
        self.factory = APIRequestFactory()
        self.view = BookListView.as_view()
        # Insert a user into the 'users' table using raw SQL
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO users (username, password) VALUES (%s, %s)
            ''', ['testuser', 'testpassword'])

        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT id FROM users WHERE username = %s
            ''', ['testuser'])
            self.user = User(id=cursor.fetchone()[0])

        # Create the 'books' table if it doesn't exist
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    author VARCHAR(200) NOT NULL,
                    genre VARCHAR(50) NOT NULL,
                    UNIQUE (title, author, genre)
                );
            ''')

        # Insert sample books with the specified conditions
        with connection.cursor() as cursor:
            cursor.executemany('''
                INSERT INTO books (title, author, genre) VALUES (%s, %s, %s)
            ''', [
                ('Book A{}'.format(i+1), 'Author {}'.format(i+1), 'Adventure')
                for i in range(6)
            ])

    def test_unauthenticated_request(self):
        """
        Test that an unauthenticated request to the BookListView returns
        a 401 Unauthorized response.
        """
        request = self.factory.get('/book/list')
        response = self.view(request)

        # Assert that the HTTP status code is 401 Unauthorized
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Expected status code 401, received %s" % response.status_code)

    def test_books_found(self):
        """
        Test that a request to the BookListView returns a 200 OK response
        containing a list of all books from the database, if any are found.

        """
        request = self.factory.get('/book/list')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        # Assert that the HTTP status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response data is as expected
        expected_books = [
            {'id': 1, 'title': 'Book A1', 'author': 'Author 1', 'genre': 'Adventure'},
            {'id': 2, 'title': 'Book A2', 'author': 'Author 2', 'genre': 'Adventure'},
            {'id': 3, 'title': 'Book A3', 'author': 'Author 3', 'genre': 'Adventure'},
            {'id': 4, 'title': 'Book A4', 'author': 'Author 4', 'genre': 'Adventure'},
            {'id': 5, 'title': 'Book A5', 'author': 'Author 5', 'genre': 'Adventure'},
            {'id': 6, 'title': 'Book A6', 'author': 'Author 6', 'genre': 'Adventure'},
        ]
        self.assertEqual(response.data, expected_books)

    def test_books_not_found(self):
        """
        Test that a request to the BookListView returns a 200 OK response
        with an empty list if no books are found in the database.

        This test case empties the database before making the request to ensure
        that no books are found.
        """
        # Empty the database using raw SQL
        with connection.cursor() as cursor:
            cursor.execute('''
                DELETE FROM books
            ''')

        # Make the request to the BookListView
        request = self.factory.get('/book/list')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        # Assert that the HTTP status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response data is an empty list
        expected_books = []
        self.assertEqual(response.data, expected_books)
