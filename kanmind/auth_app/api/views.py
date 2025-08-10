from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from auth_app.api.serializers import RegistrationUserSerializer, MailLoginSerializer
from kanban_app.api.serializers import UserShortSerializer
from core.utils.validators import validate_email_format
from core.utils.exceptions import exception_handler_status500


class RegistrationUserView(generics.CreateAPIView):
    """Creates, saves and validates new user"""
    serializer_class = RegistrationUserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            account = serializer.save()

            """Token creation"""
            token, created = Token.objects.get_or_create(user=account)

            return Response(
                {
                    "token": token.key,
                    "fullname": f"{account.first_name} {account.last_name}",
                    "email": account.email,
                    "user_id": account.id,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return exception_handler_status500(e, self.get_exception_handler_context())


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
        except Exception as e:
            return exception_handler_status500(e, self.get_exception_handler_context())
            
            
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
        except Exception as e:
            return exception_handler_status500(e, self.get_exception_handler_context())
