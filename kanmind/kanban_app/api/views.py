from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from core.utils.exceptions import exception_handler_status500
from kanban_app.models import Board, Task, Comment
from kanban_app.api.serializers import BoardListSerializer, BoardDetailSerializer, TaskSerializer, TaskCreateSerializer, CommentSerializer
from kanban_app.api.mixins import UserBoardsQuerysetMixin
from kanban_app.api.permissions import IsBoardOwnerOrMember


class BoardListCreateView(UserBoardsQuerysetMixin, generics.ListCreateAPIView):
    """View for listing and creating boards"""
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


class BoardDetailView(UserBoardsQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    """View to get, update or delete a board"""
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


class TaskCreateView(generics.CreateAPIView):
    """View to create a new task"""
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

            serializer = self.get_serializer(data=request.data, context={"request": request})
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
    """View to get all tasks assigned to the current user"""
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
    """View to get all tasks reviewed by the current user"""
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
    """View to get all tasks that the user is involved in"""
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
    """View for retrieving, updating and deleting a task"""
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


class CommentsListCreateView(APIView):
    """View for creating and listing comments"""
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

    def get_task(self, task_id):
        return get_object_or_404(Task, pk=task_id)

    def get(self, request, task_id, *args, **kwargs):
        try:
            task = self.get_task(task_id)
            self.check_object_permissions(request, task)
            comments = task.comments.select_related("author").order_by("created_at")
            return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"error": "Task nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return exception_handler_status500(exc, context=None)

    def post(self, request, task_id, *args, **kwargs):
        try:
            task = self.get_task(task_id)
            self.check_object_permissions(request, task)
            content = (request.data.get("content") or "").strip()
            if not content:
                return Response({"content": "Darf nicht leer sein."}, status=status.HTTP_400_BAD_REQUEST)
            comment = Comment.objects.create(task=task, author=request.user, content=content)
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        
        except Task.DoesNotExist:
            return Response({"error": "Task nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as exc:
            return exception_handler_status500(exc, context=None)


class CommentDeleteView(APIView):
    """Creates view for deleting a comment without GET"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, task_id, comment_id, *args, **kwargs):
        try:
            task = get_object_or_404(Task, pk=task_id)
            board = task.board
            perm = IsBoardOwnerOrMember()
            if not perm.has_object_permission(request, self, board):
                return Response({"error": perm.message}, status=status.HTTP_403_FORBIDDEN)
            comment = Comment.objects.filter(pk=comment_id, task=task).first()
            if not comment:
                return Response({"error": "Kommentar nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
            if comment.author_id != request.user.id:
                return Response({"error": "Kein Recht zum Löschen dieses Kommentars."}, status=status.HTTP_403_FORBIDDEN)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Task.DoesNotExist:
            return Response({"error": "Task nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as exc:
            return exception_handler_status500(exc, context=None)
