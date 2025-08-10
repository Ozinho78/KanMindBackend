from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from auth_app.api.serializers import RegistrationUserSerializer, MailLoginSerializer
from kanban_app.api.serializers import UserShortSerializer
from core.utils.validators import validate_email_format, validate_email_unique, validate_fullname, validate_password_strength
from core.utils.exceptions import exception_handler_status500


class RegistrationUserView(generics.CreateAPIView):
    """Creates, saves and validates new user"""
    serializer_class = RegistrationUserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            fullname = request.data.get("fullname", "").strip()
            email = request.data.get("email", "").strip()
            password = request.data.get("password", "")
            repeated_password = request.data.get("repeated_password", "")

            """Validations from validators.py"""
            validate_fullname(fullname)
            validate_email_format(email)
            validate_email_unique(email)

            if password != repeated_password:
                error_message = {
                    "password": "Passwörter stimmen nicht überein."}
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

            validate_password_strength(password)

            """Splitting fullname"""
            first_name, last_name = fullname.split(" ", 1)

            """Save user"""
            serializer = self.get_serializer(data={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name
            })
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            """Create token"""
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "token": token.key,
                    "fullname": f"{first_name} {last_name}",
                    "email": user.email,
                    "user_id": user.id
                },
                status=status.HTTP_201_CREATED
            )

        except:
            exception_handler_status500()


class MailLoginView(APIView):
    """Logs in a user with valid credentials"""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = MailLoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            account = serializer.validated_data["user"]
            
            """Request Token or create Token"""
            token, created = Token.objects.get_or_create(user=account)
            
            return Response(
                {
                    "token": token.key,
                    "fullname": f"{account.first_name} {account.last_name}",
                    "email": account.email,
                    "user_id": account.id
                },
                status=status.HTTP_200_OK
            )
        except:
            exception_handler_status500()
            
            
class MailCheckView(APIView):
    """Checks if email is already in use."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            email = request.query_params.get("email", "").strip()
            if not email:
                return Response({"error": "E-Mail-Adresse fehlt."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                validate_email_format(email)
            except:
                return Response({"error": "Ungültige E-Mail-Adresse."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(email=email)
                serializer = UserShortSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "E-Mail nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        except:
            return exception_handler_status500()
