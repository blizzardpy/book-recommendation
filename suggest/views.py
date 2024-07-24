from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import connection

from book.models import Book
from book.serializers import BookSerializer


class SuggestBookView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer

    """
    Get a list of suggested books for the authenticated user based on their preferred genres.

    The function queries the database to find the user's preferred genres based on the highest average rating.
    Then it fetches books from those genres that the user hasn't reviewed yet.

    Returns:
        Response: The HTTP response containing the list of suggested books or an error message.
            The response status code is 200 if the suggested books are found, otherwise 404.
            The response data is a JSON object containing the serialized book data or an error message.
    """

    def get(self, request, *args, **kwargs):
        user_id = request.user.id

        with connection.cursor() as cursor:
            # Determine the user's preferred genres based on highest average rating
            cursor.execute("""
                SELECT b.genre, AVG(r.rating) as avg_rating
                FROM books b
                JOIN reviews r ON b.id = r.book_id
                WHERE r.user_id = %s
                GROUP BY b.genre
                ORDER BY avg_rating DESC
            """, [user_id])
            genre_ratings = cursor.fetchall()

            if genre_ratings:
                max_avg_rating = genre_ratings[0][1]
                preferred_genres = [row[0]
                                    for row in genre_ratings if row[1] == max_avg_rating]

                if preferred_genres:
                    # Fetch books from the user's preferred genres that they haven't reviewed
                    cursor.execute("""
                        SELECT b.id, b.title, b.author, b.genre
                        FROM books b
                        WHERE b.genre IN %s
                        AND b.id NOT IN (
                            SELECT book_id
                            FROM reviews
                            WHERE user_id = %s
                        )
                    """, [tuple(preferred_genres), user_id])
                    books = cursor.fetchall()

                    if books:
                        # Create a list of Book objects from the fetched rows
                        books = [
                            Book(
                                id=row[0], title=row[1],
                                author=row[2], genre=row[3])
                            for row in books
                        ]

                        # Serialize the books and return the response
                        serializer = self.serializer_class(books, many=True)
                        return Response(serializer.data, status=status.HTTP_200_OK)

                    else:
                        # Return an error message if no book suggestions are found
                        return Response(
                            {"detail": "No book suggestions available for the preferred genres."},
                            status=status.HTTP_404_NOT_FOUND)
            # Return an error message if no preferred genres are found
            return Response({"detail": "No preferred genres found"}, status=status.HTTP_404_NOT_FOUND)
