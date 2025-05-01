from django.shortcuts import render
from rest_framework.views import APIView
from .models import User
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from .serializers import *
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import JsonResponse


class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class MyRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token['sub'] = {
            'id': user.id,
            'fullname': user.full_name
        }
        return token


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "Неправильний email або пароль"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not bcrypt.checkpw(password.encode(), user.hash_password.encode()):
            return JsonResponse(
                {"error": "Неправильний email або пароль"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = MyRefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return JsonResponse(
            {
                "payloadType": "LoginResponseDto",
                "payload": {
                    "accessToken": access_token
                }
            },
            status=status.HTTP_200_OK
        )
