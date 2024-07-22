from rest_framework import serializers

from authentication.models import User


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        read_only_fields = ['id']
        write_only_fields = ['password']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']
