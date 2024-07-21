from rest_framework import serializers

from .models import User, Book


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        read_only_fields = ['id']
        write_only_fields = ['password']


class BookSerializer(serializers.Serializer):

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre']
