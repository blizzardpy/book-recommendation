from django.db import connection
from django.http import Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from review.models import Review
from review.serializers import ReviewSerializer, UpdateReviewSerializer


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
    serializer_class = UpdateReviewSerializer
    lookup_field = 'id'

    """
    View for updating a review.

    This view handles HTTP PUT requests to update an existing review. It requires
    the user to be authenticated. The view expects the review ID in the URL path
    and the updated review data in the request body.

    Attributes:
        permission_classes (list): A list containing the permission class
            IsAuthenticated, which ensures that only authenticated users can
            update a review.
        serializer_class (class): The serializer class used to validate and
            serialize the updated review data.
        lookup_field (str): The field used to look up the review in the URL
            path, which is 'id'.
    """

    def get_object(self):
        """
        Get the review object to be updated.

        This method retrieves the review object identified by the ID in the URL
        path and locks it for update. If the review is not found, it raises an
        Http404 exception.

        Returns:
            Review: The review object to be updated.

        Raises:
            Http404: If the review is not found.
        """
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


class DestroyReviewView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    lookup_field = 'id'

    """
    View for deleting a review.

    This view handles HTTP DELETE requests to delete an existing review. It
    requires the user to be authenticated. The view expects the review ID in
    the URL path.

    Attributes:
        permission_classes (list): A list containing the permission class
            IsAuthenticated, which ensures that only authenticated users can
            delete a review.
        serializer_class (class): The serializer class used to validate and
            serialize the review data.
        lookup_field (str): The field used to look up the review in the URL
            path, which is 'id'.
    """

    def get_object(self):
        """
        Get the review object to be deleted.

        This method retrieves the review object identified by the ID in the URL
        path and locks it for update. If the review is not found, it raises an
        Http404 exception.

        Returns:
            Review: The review object to be deleted.

        Raises:
            Http404: If the review is not found.
        """
        # Get the review ID from the URL path
        review_id = self.kwargs.get('id')

        # Execute a SQL query to retrieve the review and lock it for update
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
            # Fetch the review from the query result
            row = cursor.fetchone()

            # If the review is not found, raise an Http404 exception
            if not row:
                raise Http404("Review not found.")
            return Review(id=row[0], rating=row[1], book_id=row[2], user_id=row[3])


class UserReviewsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    """
    View for getting a list of reviews created by the authenticated user.

    This view handles HTTP GET requests to retrieve a list of reviews created
    by the authenticated user. It requires the user to be authenticated. The
    view returns a list of review objects for the authenticated user.

    Attributes:
        permission_classes (list): A list containing the permission class
            IsAuthenticated, which ensures that only authenticated users can
            get a list of reviews.
        serializer_class (class): The serializer class used to serialize the
            review data.
    """

    def get_queryset(self):
        """
        Get a list of all reviews created by the authenticated user.

        Returns:
            QuerySet: A queryset of Review objects.
        """
        # Get the user id from the request
        user_id = self.request.user.id

        # Execute a SQL query to retrieve all reviews created by the user
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, rating, book_id, user_id
                FROM reviews
                WHERE user_id = %s
                """,
                [user_id]
            )
            rows = cursor.fetchall()

        # Create a list of Review objects from the fetched rows
        return [Review(id=row[0], rating=row[1], book_id=row[2], user_id=row[3]) for row in rows]
