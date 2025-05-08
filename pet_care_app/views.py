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


class CalendarEventListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        pet_id = request.query_params.get('pet')
        events = CalendarEvent.objects.filter(
            pet__user=request.user,
            start_date__year=year,
            start_date__month=month,
            **({'pet__id': pet_id} if pet_id else {})
        )
        serializer = CalendarEventSerializer(events, many=True)
        return JsonResponse({'payloadType': 'CalendarListDto', 'payload': serializer.data})

    def post(self, request):
        serializer = CalendarEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pet = get_object_or_404(Pet, pk=request.data['pet'], user=request.user)
        serializer.save(pet=pet)
        return JsonResponse({'payloadType': 'CalendarDto', 'payload': serializer.data}, status=201)


class CalendarEventDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def put(self, request, pk):
        event = get_object_or_404(CalendarEvent, pk=pk, pet__user=request.user)
        serializer = CalendarEventSerializer(event, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({'payloadType': 'CalendarDto', 'payload': serializer.data})

    def patch(self, request, pk):
        event = get_object_or_404(CalendarEvent, pk=pk, pet__user=request.user)
        serializer = CalendarEventSerializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({'payloadType': 'CalendarDto', 'payload': serializer.data})

    def delete(self, request, pk):
        event = get_object_or_404(CalendarEvent, pk=pk, pet__user=request.user)
        event.delete()
        return JsonResponse({}, status=204)


class JournalEntryListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        entries = JournalEntry.objects.filter(pet__user=request.user).order_by('-created_at')
        serializer = JournalEntrySerializer(entries, many=True)
        return JsonResponse({'payloadType': 'JournalListDto', 'payload': serializer.data})

    def post(self, request):
        serializer = JournalEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pet = get_object_or_404(Pet, pk=request.data.get('pet'), user=request.user)
        serializer.save(pet=pet)

        return JsonResponse({'payloadType': 'JournalDto', 'payload': serializer.data},
                            status=status.HTTP_201_CREATED)


class JournalEntryDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def put(self, request, pk):
        entry = get_object_or_404(JournalEntry, pk=pk, pet__user=request.user)
        serializer = JournalEntrySerializer(entry, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({'payloadType': 'JournalDto', 'payload': serializer.data})

    def patch(self, request, pk):
        entry = get_object_or_404(JournalEntry, pk=pk, pet__user=request.user)
        serializer = JournalEntrySerializer(entry, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({'payloadType': 'JournalDto', 'payload': serializer.data})

    def delete(self, request, pk):
        entry = get_object_or_404(JournalEntry, pk=pk, pet__user=request.user)
        entry.delete()
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


class SitePartnerListView(generics.ListAPIView):
    queryset = SitePartner.objects.all()
    serializer_class = SitePartnerSerializer
    permission_classes = [permissions.IsAuthenticated]