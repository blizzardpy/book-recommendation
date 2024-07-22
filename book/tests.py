from django.db import connection
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework import status

from auth.models import User
from book.views import BookListView, BooksListByGenreView


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
            {'id': 19, 'title': 'Book A1', 'author': 'Author 1', 'genre': 'Adventure'},
            {'id': 20, 'title': 'Book A2', 'author': 'Author 2', 'genre': 'Adventure'},
            {'id': 21, 'title': 'Book A3', 'author': 'Author 3', 'genre': 'Adventure'},
            {'id': 22, 'title': 'Book A4', 'author': 'Author 4', 'genre': 'Adventure'},
            {'id': 23, 'title': 'Book A5', 'author': 'Author 5', 'genre': 'Adventure'},
            {'id': 24, 'title': 'Book A6', 'author': 'Author 6', 'genre': 'Adventure'},
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


class BookListByGenreViewTestCase(TestCase):

    def setUp(self):
        """
        Set up the test case by creating the 'books' table and inserting
        sample books with the specified conditions.
        """
        self.factory = APIRequestFactory()
        self.view = BooksListByGenreView.as_view()
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
                ('Book A{}'.format(i+1), 'Author {}'.format(i+1), 'Science')
                for i in range(6)
            ])

    def test_unauthenticated_request(self):
        """
        Test that an unauthenticated request to the BookListView returns
        a 401 Unauthorized response.
        """
        request = self.factory.get('/book/?genre=Science')
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
        request = self.factory.get('/book/?genre=Science')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        # Assert that the HTTP status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response data is as expected
        expected_books = [
            {'id': 1, 'title': 'Book A1', 'author': 'Author 1', 'genre': 'Science'},
            {'id': 2, 'title': 'Book A2', 'author': 'Author 2', 'genre': 'Science'},
            {'id': 3, 'title': 'Book A3', 'author': 'Author 3', 'genre': 'Science'},
            {'id': 4, 'title': 'Book A4', 'author': 'Author 4', 'genre': 'Science'},
            {'id': 5, 'title': 'Book A5', 'author': 'Author 5', 'genre': 'Science'},
            {'id': 6, 'title': 'Book A6', 'author': 'Author 6', 'genre': 'Science'},
        ]
        self.assertEqual(response.data, expected_books)

    def test_books_not_found(self):
        """
        Test that a request to the BookListView returns a 200 OK response
        with an empty list if no books are found in the database.

        This test case empties the database before making the request to ensure
        that no books are found.
        """
        # # Empty the database using raw SQL
        with connection.cursor() as cursor:
            cursor.execute('''
                DELETE FROM books
                WHERE genre = %s
            ''', ['Science'])

        # Make the request to the BookListView
        request = self.factory.get('/book/?genre=Adventure')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        # Assert that the HTTP status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response data is an empty list
        expected_books = []
        self.assertEqual(response.data, expected_books)
