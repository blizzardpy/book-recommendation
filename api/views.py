from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class LoginView(APIView):

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
