from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from kanban_app.api.serializers import RegistrationUserSerializer, EmailLoginSerializer, BoardListSerializer, BoardDetailSerializer
from kanban_app.utils.validators import validate_email_format, validate_email_unique, validate_fullname, validate_password_strength
from kanban_app.api.mixins import UserBoardsQuerysetMixin
from kanban_app.api.permissions import IsBoardOwnerOrMember


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
                error_message = {"password": "Passwörter stimmen nicht überein."}
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

            if not created:
                error_message = {"token": "Ein Token für diesen Benutzer existiert bereits."}
                return Response(error_message, status=status.HTTP_409_CONFLICT)

            return Response(
                {
                    "token": token.key,
                    "fullname": f"{first_name} {last_name}",
                    "email": user.email,
                    "user_id": user.id
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({"details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = EmailLoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            account = serializer.validated_data["user"]

            """Request Token"""
            token = Token.objects.filter(user=account).first()
            if not token:
                return Response({"error": "Kein Token vorhanden."}, status=status.HTTP_409_CONFLICT)

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
            return Response({"error": "Interner Serverfehler"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BoardListCreateView(UserBoardsQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardListSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Interner Serverfehler"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        try:
            serializer.save(owner=self.request.user)
        except Exception:
            return Response({"error": "Fehler beim Erstellen des Boards"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BoardDetailView(UserBoardsQuerysetMixin, generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]
    serializer_class = BoardDetailSerializer
    

                                
