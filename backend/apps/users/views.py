from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from .serializers import RegisterSerializer

from rest_framework.permissions import IsAuthenticated

from .models import User

class RegisterView(APIView):

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {"message": "User created successfully"},
                status=status.HTTP_201_CREATED
            )

        print(serializer.errors)   # Pour voir l'erreur dans le terminal

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
class LoginView(APIView):

    def post(self, request):

        print("=================================")
        print("🔥 LOGIN VIEW APPELEE")
        print("DATA RECUE :", request.data)
        print("=================================")

        serializer = LoginSerializer(data=request.data)

        print("SERIALIZER VALID :", serializer.is_valid())
        print("SERIALIZER ERRORS :", serializer.errors)

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            })

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            return Response({

                "refresh": str(refresh),

                "access": str(refresh.access_token),

                "first_name": user.first_name,

                "last_name": user.last_name,

                "email": user.email

            })

        return Response(
            serializer.errors,
            status=400
        )



class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        return Response({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "city": user.city,
            "birth_date": user.birth_date,
            "profile_image": (
                request.build_absolute_uri(user.profile_image.url)
                if user.profile_image
                else None
            ),
        })