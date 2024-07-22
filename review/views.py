from django.db import connection
from django.http import Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from review.models import Review
from review.serializers import ReviewSerializer


class CreateReviewView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    """
    API View to create a review.

    This view requires authentication. It expects a POST request with a JSON body
    containing the review data. The review data should include the book ID and
    rating. The user ID is automatically set to the ID of the
    authenticated user.

    On successful creation, the view returns a JSON response with the serialized
    review data and a status code of 201 Created.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle HTTP POST request for creating a review.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response:
                The HTTP response object containing the serialized review
                data and a status code of 201 Created.
        """
        # Get the serializer with the request data
        serializer = self.serializer_class(
            data=request.data, context={'request': request})

        # Validate the data and raise an exception if invalid
        serializer.is_valid(raise_exception=True)

        # Save the validated data to the database
        serializer.save()

        # Return a response with the serialized data and a status code of 201 Created
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateReviewView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    lookup_field = 'id'

    def get_object(self):
        review_id = self.kwargs.get('id')
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, rating, book_id, user_id
                FROM reviews
                WHERE id = %s
                FOR UPDATE OF reviews;
                """,
                [review_id]
            )
            row = cursor.fetchone()
            if not row:
                raise Http404("Review not found.")
            return Review(id=row[0], rating=row[1], book_id=row[2], user_id=row[3])
