from rest_framework import serializers

from book.models import Book


class BookSerializer(serializers.Serializer):

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre']
