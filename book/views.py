from django.db import connection
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from book.serializers import BookSerializer


class BookListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer

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
    serializer_class = BookSerializer

    genre_param_config = openapi.Parameter(
        'genre',
        in_=openapi.IN_QUERY,
        description='Filter by genre',
        type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[genre_param_config,])
    def get(self, request, *args, **kwargs):
        """
        Retrieve a list of all books from the database that match the specified genre.

        Returns:
            Response: The HTTP response containing the list of books or an empty list.
        """
        # Get the genre from the request
        genre = request.GET.get('genre', None)

        if not genre:
            # Return an empty list if no genre is provided
            return Response([])

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
