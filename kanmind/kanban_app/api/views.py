from django.contrib.auth.models import User
from django.db import models
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from kanban_app.models import Board, Task
from kanban_app.api.serializers import RegistrationUserSerializer, EmailLoginSerializer, BoardListSerializer, BoardDetailSerializer, UserShortSerializer, TaskSerializer, TaskCreateSerializer
from kanban_app.utils.validators import validate_email_format, validate_email_unique, validate_fullname, validate_password_strength
from kanban_app.utils.exceptions import exception_handler_status500
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

            # if not created:
            #     error_message = {"token": "Ein Token für diesen Benutzer existiert bereits."}
            #     return Response(error_message, status=status.HTTP_409_CONFLICT)

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


class EmailLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = EmailLoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            account = serializer.validated_data["user"]

            """Request Token or create Token"""
            # token = Token.objects.filter(user=account).first()
            # if not token:
            #     return Response({"error": "Kein Token vorhanden."}, status=status.HTTP_409_CONFLICT)
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


class BoardListCreateView(UserBoardsQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardListSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            error_message = {"error": "Interner Serverfehler"}
            return Response(error_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        try:
            serializer.save(owner=self.request.user)
        except:
            exception_handler_status500()
            # error_message = {"error": "Interner Serverfehler"}
            # return Response(error_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BoardDetailView(UserBoardsQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]
    serializer_class = BoardDetailSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            board = self.get_object()
            board.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Board.DoesNotExist:
            return Response({"error": "Board nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        except:
            return exception_handler_status500()


class MailCheckView(APIView):
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


class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

    def create(self, request, *args, **kwargs):
        try:
            board_id = request.data.get("board")
            if not board_id:
                return Response({"board": "Dieses Feld wird benötigt."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                return Response({"error": "Board nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)

            self.check_object_permissions(request, board)

            assignee_id = request.data.get("assignee_id")
            reviewer_id = request.data.get("reviewer_id")

            allowed_user_ids = list(board.members.values_list("id", flat=True)) + [board.owner.id]
            errors = {}

            if assignee_id and int(assignee_id) not in allowed_user_ids:
                errors["assignee_id"] = "Assignee ist kein Mitglied dieses Boards."
            if reviewer_id and int(reviewer_id) not in allowed_user_ids:
                errors["reviewer_id"] = "Reviewer ist kein Mitglied dieses Boards."
            if errors:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(
                data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            task = serializer.save()

            try:
                response_serializer = TaskSerializer(task)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response({"error": "Fehler beim Serialisieren des Tasks"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except:
            return exception_handler_status500()


class TasksAssignedToMeView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return exception_handler_status500(e, self.get_exception_handler_context())


class TasksReviewedByMeView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return exception_handler_status500(e, self.get_exception_handler_context())


class TasksInvolvedView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            models.Q(assignee=self.request.user) |
            models.Q(reviewer=self.request.user)
        ).distinct()

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return exception_handler_status500(e, self.get_exception_handler_context())


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

    def get_object(self):
        task = super().get_object()
        """Permission check for respective board"""
        self.check_object_permissions(self.request, task.board)
        return task

    def patch(self, request, *args, **kwargs):
        try:
            task = self.get_object()

            """Checks valid assignee and reviewer"""
            assignee_id = request.data.get("assignee_id")
            reviewer_id = request.data.get("reviewer_id")
            allowed_user_ids = list(task.board.members.values_list("id", flat=True)) + [task.board.owner.id]
            errors = {}

            if assignee_id and int(assignee_id) not in allowed_user_ids:
                errors["assignee_id"] = "Assignee ist kein Mitglied dieses Boards."
            if reviewer_id and int(reviewer_id) not in allowed_user_ids:
                errors["reviewer_id"] = "Reviewer ist kein Mitglied dieses Boards."
            if errors:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

            """Partial (PATCH) update"""
            serializer = self.get_serializer(task, data=request.data, partial=True, context={"request": request})
            serializer.is_valid(raise_exception=True)
            updated_task = serializer.save()

            response_serializer = TaskSerializer(updated_task)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Task.DoesNotExist:
            return Response({"error": "Task nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return exception_handler_status500(e, self.get_exception_handler_context())

    def delete(self, request, *args, **kwargs):
        try:
            task = self.get_object()
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response({"error": "Task nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return exception_handler_status500(e, self.get_exception_handler_context())
