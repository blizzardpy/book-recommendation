from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory
from django.db import connection
from rest_framework.test import force_authenticate

from review.views import CreateReviewView
from authentication.models import User


class TestCreateReviewView(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = CreateReviewView.as_view()
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

        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO books (title, author, genre) VALUES (%s, %s, %s)
            ''', ['Test Title', 'Test Author', 'Test Genre'])

        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT id FROM books WHERE title = %s
            ''', ['Test Title'])
            self.book_id = cursor.fetchone()[0]

    def test_unauthenticated_request(self):
        """
        Test to ensure an unauthenticated request is appropriately rejected.

        This method tests the application's behavior when an unauthenticated
        request is made to a protected view. It verifies that the response
        is a 401 Unauthorized, indicating that the request was correctly
        identified as unauthenticated and thus not allowed to proceed.
        """

        # Create an unauthenticated request to the review endpoint
        request = self.factory.get('/api/review/')

        # Process the request using the view under test
        response = self.view(request)

        # Verify the response has a status code of 401, indicating unauthorized access
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Expected status code 401, received %s" % response.status_code)

    def test_create_review_success(self):
        """
        Test to ensure a review can be successfully created.

        This method tests the application's behavior when a valid review
        request is made to the view. It verifies that the response is a
        201 Created, indicating that the review was successfully created.
        """

        # Create a valid review request
        request = self.factory.post(
            # The URL to the view under test
            '/api/review/',
            # The data to be sent in the request
            {'rating': 4, 'book': self.book_id})

        # Force authenticate the request with the user
        force_authenticate(request, user=self.user)

        # Process the request using the view under test
        response = self.view(request)

        # The expected review object returned by the view
        expected_review = {
            'id': 2,
            'rating': 4,
            'book': self.book_id,
            'user': self.user.id
        }

        # Verify the response data contains the expected review
        self.assertEqual(
            # The response data
            response.data,
            # The expected review
            expected_review,
            # The message if the assertion fails
            "Expected response data %s, received %s" %
            (expected_review, response.data))

        # Verify the response has a status code of 201, indicating the review was created
        self.assertEqual(
            # The response status code
            response.status_code,
            # The expected status code
            status.HTTP_201_CREATED,
            # The message if the assertion fails
            "Expected status code 201, received %s" % response.status_code)

    def test_create_review_invalid_data_rating_value_incorrect(self):
        """
        Test that an invalid request to create a review with a rating value
        greater than 5 returns a 400 Bad Request response with an error message.
        """
        # Create an invalid review request
        request = self.factory.post(
            '/api/review/', {'rating': 6, 'book': self.book_id})
        # Force authenticate the request with the user
        force_authenticate(request, user=self.user)
        # Process the request using the view under test
        response = self.view(request)
        # The expected error message
        expected = {'rating': [
            'Ensure this value is less than or equal to 5.']}
        # Verify the response data contains the expected error message
        self.assertEqual(
            response.data, expected,
            "Expected response data %s, received %s" %
            (expected, response.data))
        # Verify the response has a status code of 400 Bad Request
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "Expected status code 400, received %s" % response.status_code)

    def test_review_invalid_data_book_not_found(self):
        """
        Test that an invalid request to create a review with a non-existent book
        returns a 400 Bad Request response with an error message.
        """
        # Create an invalid review request
        request = self.factory.post(
            # The URL to the view under test
            '/api/review/',
            # The data to be sent in the request
            {'rating': 3, 'book': self.book_id + 1})

        # Force authenticate the request with the user
        force_authenticate(request, user=self.user)

        # Process the request using the view under test
        response = self.view(request)

        # Verify the response has a status code of 400 Bad Request
        self.assertEqual(
            # The response status code
            response.status_code,
            # The expected status code
            status.HTTP_400_BAD_REQUEST,
            # The message if the assertion fails
            "Expected status code 400, received %s" % response.status_code)

    def test_create_review_already_exist(self):
        """
        Test that an attempt to create a review with the same book and user
        returns a 400 Bad Request response with an error message.
        """
        # Create a request to create a review with the same book and user
        request = self.factory.post(
            '/api/review/', {'rating': 4, 'book': self.book_id})
        force_authenticate(request, user=self.user)

        response = self.view(request)

        # Process the request using the view under test, which should fail
        # since the user has already reviewed the book
        response = self.view(request)

        # Verify the response has a status code of 400 Bad Request
        self.assertEqual(
            # The response status code
            response.status_code,
            # The expected status code
            status.HTTP_400_BAD_REQUEST,
            # The message if the assertion fails
            "Expected status code 400, received %s" % response.status_code)
