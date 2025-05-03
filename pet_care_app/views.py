from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from .serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.authentication import get_authorization_header
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated



class MyRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token['sub'] = {
            'id': user.id,
            'fullname': user.full_name
        }
        return token


class SignInView(APIView):
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

        if not check_password(password, user.password):
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


class SignUpView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = MyRefreshToken.for_user(user)
        access = refresh.access_token

        return JsonResponse(
            {
                "payloadType": "RegistrationResponseDto",
                "payload": {
                    "accessToken": str(access),
                }
            },
            status=status.HTTP_201_CREATED
        )


class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return JsonResponse(
            {
                "payloadType": "UserInfoDto",
                "payload": serializer.data
            },
            status=status.HTTP_200_OK
        )
