from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User
from api.serializers import UserSerializer, BookSerializer


class LoginView(APIView):
    # serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle HTTP POST request for login.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response:
                The HTTP response object containing the user information,
                refresh token, and access token. If the credentials are
                invalid, an error message is returned.
        """
        # Get the username and password from the request data
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if the username and password are provided
        if not username or not password:
            # Return an error response if the username or password is missing
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST)

        # Query the database for the user credentials
        with connection.cursor() as cursor:
            # Execute the SQL query to check if the user exists
            cursor.execute(
                'SELECT id, password FROM users WHERE username = %s', [username])
            row = cursor.fetchone()

        # Check if the user exists in the database
        if row is not None:
            user_id, user_password = row

            # Check if the password is correct
            if password == user_password:
                # Create a user object with the retrieved information
                user = User(id=user_id, username=username)
                # Generate refresh and access tokens
                refresh_token = RefreshToken.for_user(user)
                # Return a success response with the user information, refresh token, and access token
                return Response({
                    'user': {
                        'id': user.id,
                        'username': user.username
                    },
                    'refresh': str(refresh_token),
                    'access': str(refresh_token.access_token),
                }, status=status.HTTP_200_OK)

        # Return an error response if the credentials are invalid
        return Response(
            {'error': 'Invalid Credentials'},
            status=status.HTTP_401_UNAUTHORIZED)


class BookListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    # serializer_class = BookSerializer

    def get(self, request, *args, **kwargs):
        """
        Retrieve a list of all books from the database or an empty list if no books are found.

        Returns:
            Response: The HTTP response containing the list of books or an empty list.
        """
        # Execute the SQL query to retrieve all books
        with connection.cursor() as cursor:
            cursor.execute('SELECT id, title, author, genre FROM books')
            rows = cursor.fetchall()

        # Check if any books are found
        if rows:
            # Create a list of dictionaries containing the book information
            books = [
                {'id': row[0], 'title': row[1],
                    'author': row[2], 'genre': row[3]}
                for row in rows
            ]
        else:
            # Return an empty list if no books are found
            books = []

        # Return the list of books as a JSON response
        return Response(
            books,  # The data to be serialized into JSON
            status=status.HTTP_200_OK  # The HTTP status code
        )


class BooksListByGenreView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    # serializer_class = BookSerializer

    def get(self, request, *args, **kwargs):
        """
        Retrieve a list of all books from the database that match the specified genre.

        Returns:
            Response: The HTTP response containing the list of books or an empty list.
        """
        # Get the genre from the request
        genre = request.query_params.get('genre')

        # Execute the SQL query to retrieve all books with the specified genre
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT id, title, author, genre FROM books WHERE genre = %s', [genre])
            rows = cursor.fetchall()

        # Check if any books are found
        if rows:
            # Create a list of dictionaries containing the book information
            books = [
                {'id': row[0], 'title': row[1],
                    'author': row[2], 'genre': row[3]}
                for row in rows
            ]
        else:
            # Return an empty list if no books are found
            books = []

        # Return the list of books as a JSON response
        return Response(
            books,  # The data to be serialized into JSON
            status=status.HTTP_200_OK  # The HTTP status code
        )
