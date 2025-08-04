from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import RegistrationUserSerializer, EmailLoginSerializer
from kanban_app.utils.validators import (
    validate_email_format,
    validate_email_unique,
    validate_fullname,
    validate_password_strength
)


class RegistrationUserView(generics.CreateAPIView):
    serializer_class = RegistrationUserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            fullname = request.data.get("fullname", "").strip()
            email = request.data.get("email", "").strip()
            password = request.data.get("password", "")
            repeated_password = request.data.get("repeated_password", "")

            # --- Validierungen ---
            validate_fullname(fullname)
            validate_email_format(email)
            validate_email_unique(email)

            if password != repeated_password:
                return Response(
                    {"password": "Passwörter stimmen nicht überein."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            validate_password_strength(password)

            # --- Fullname splitten ---
            first_name, last_name = fullname.split(" ", 1)

            # --- User speichern ---
            serializer = self.get_serializer(data={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name
            })
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # --- Token erstellen ---
            token, created = Token.objects.get_or_create(user=user)

            if not created:
                return Response(
                    {"token": "Ein Token für diesen Benutzer existiert bereits – bitte Administrator kontaktieren."},
                    status=status.HTTP_409_CONFLICT
                )

            return Response(
                {
                    "message": "Der Benutzer wurde erfolgreich erstellt.",
                    "token": token.key,
                    "fullname": f"{first_name} {last_name}",
                    "email": user.email,
                    "user_id": user.id
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {
                    "message": "Interner Serverfehler.",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmailLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = EmailLoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"message": "Ungültige Anfragedaten.", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = serializer.validated_data["user"]

            # Token nur abrufen, nicht neu erstellen
            token = Token.objects.filter(user=user).first()
            if not token:
                return Response(
                    {"message": "Kein Token vorhanden – bitte Administrator kontaktieren."},
                    status=status.HTTP_409_CONFLICT
                )

            return Response(
                {
                    "token": token.key,
                    "fullname": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "user_id": user.id
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": "Interner Serverfehler.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )















          

# class LoginView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request, *args, **kwargs):
#         try:
#             serializer = LoginSerializer(data=request.data)
#             if not serializer.is_valid():
#                 return Response(
#                     {"message": "Ungültige Anfragedaten.", "errors": serializer.errors},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             user = serializer.validated_data["user"]

#             # Token abrufen – keinen neuen erstellen
#             token = Token.objects.filter(user=user).first()
#             if not token:
#                 return Response(
#                     {"message": "Kein Token vorhanden - bitte Administrator kontaktieren."},
#                     status=status.HTTP_409_CONFLICT
#                 )

#             return Response(
#                 {
#                     "message": "Login erfolgreich.",
#                     "token": token.key,
#                     "fullname": f"{user.first_name} {user.last_name}",
#                     "email": user.email,
#                     "user_id": user.id
#                 },
#                 status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response(
#                 {"message": "Interner Serverfehler.", "details": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


# class RegistrationUserView(generics.CreateAPIView):
#     serializer_class = RegistrationUserSerializer
#     permission_classes = [permissions.AllowAny]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user_data = serializer.save()
#         return Response(user_data, status=status.HTTP_201_CREATED)
