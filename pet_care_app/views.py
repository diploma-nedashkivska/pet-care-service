from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from .models import *
from .serializers import *
from rest_framework import status, viewsets, permissions, generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.authentication import get_authorization_header
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from django.shortcuts import get_object_or_404

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




class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        user = serializer.save()
        pwd = self.request.data.get('password')
        if pwd:
            user.set_password(pwd)
            user.save()


class PetListCreateView(APIView):
    """
    GET  /pets/   — список усіх своїх тварин у payload: [...]
    POST /pets/   — передати форму, створити, повернути в payload: {…}
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # ← сюди

    def get(self, request):
        pets = Pet.objects.filter(user=request.user)
        serializer = PetSerializer(pets, many=True)
        return JsonResponse({
            "payloadType": "PetListDto",
            "payload": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return JsonResponse({
            "payloadType": "PetDto",
            "payload": serializer.data
        }, status=status.HTTP_201_CREATED)


class PetDetailView(APIView):
    """
    PUT    /pets/{pk}/   — повне оновлення
    PATCH  /pets/{pk}/   — часткове оновлення
    DELETE /pets/{pk}/   — видалення
    (теж повертають payload з об’єктом або 204 No Content)
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # ← сюди


    def put(self, request, pk):
        pet = get_object_or_404(Pet, pk=pk, user=request.user)
        serializer = PetSerializer(pet, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({
            "payloadType": "PetDto",
            "payload": serializer.data
        })

    def patch(self, request, pk):
        pet = get_object_or_404(Pet, pk=pk, user=request.user)
        serializer = PetSerializer(pet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({
            "payloadType": "PetDto",
            "payload": serializer.data
        })

    def delete(self, request, pk):
        pet = get_object_or_404(Pet, pk=pk, user=request.user)
        pet.delete()
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)