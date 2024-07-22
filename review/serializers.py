from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import connection

from authentication.serializers import UserSerializer
from review.models import Review
from book.serializers import BookSerializer


class ReviewSerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField(validators=[MinValueValidator(1)], write_only=True)
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = serializers.SerializerMethodField()
    book = serializers.SerializerMethodField()

    def get_book(self, obj):
        return BookSerializer(obj.book).data

    def get_user(self, obj):
        return UserSerializer(obj.user).data

    class Meta:
        model = Review
        fields = ['id', 'rating', 'book', 'user', 'book_id']
        extra_kwargs = {
            'book_id': {'write_only': True},
            'user': {'read_only': True},
        }

    def validate(self, data):
        """
        Validate the review data.

        This method checks if the book to be reviewed exists in the database
        and ensures that the user has not already reviewed the book. If the book does
        not exist or the user has already reviewed the book, it raises a ValidationError.

        Args:
            data (dict): The incoming data to validate. It must contain 'book_id'.

        Returns:
            dict: The validated data including the 'user_id' obtained from the request context.

        Raises:
            serializers.ValidationError: If the book does not exist or the user has already reviewed the book.
        """
        # Check if the book exists in the database
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM books
                WHERE id = %s
                """,
                [data['book_id']]
            )
            count = cursor.fetchone()[0]
            if count == 0:
                # If the book does not exist, raise an error
                raise serializers.ValidationError('Book does not exist')

        # Add current user id to data
        data['user_id'] = self.context['request'].user.id

        if self.context['request'].method == 'POST':
            # Check if the user has already reviewed the book
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM reviews
                    WHERE book_id = %s
                    AND user_id = %s
                    """,
                    (data['book_id'], data['user_id'])
                )
                count = cursor.fetchone()[0]
                if count > 0:
                    # If the user has already reviewed the book, raise an error
                    raise serializers.ValidationError(
                        'User has already reviewed this book')

        # Return validated data
        return data

    def create(self, validated_data):
        """
        Create a new Review object in the database.

        Args:
            validated_data (dict): The validated data for creating a new Review object.

        Returns:
            review.models.Review: The newly created Review object.

        Raises:
            None.
        """
        # Insert a new review into the database
        with connection.cursor() as cursor:
            # Use a parameterized query to prevent SQL injection
            cursor.execute(
                """
                INSERT INTO reviews (rating, book_id, user_id)
                VALUES (%s, %s, %s)
                RETURNING id, rating, book_id, user_id;
                """,
                (validated_data['rating'], validated_data['book_id'],
                 validated_data['user_id'])
            )
            # Fetch the newly created review from the database
            row = cursor.fetchone()
            # Create a new Review object with the fetched data
            return Review(id=row[0], rating=row[1], book_id=row[2], user_id=row[3])
