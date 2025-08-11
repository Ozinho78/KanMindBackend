from django.db.models import Count
from django.db.models.functions import Coalesce
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from core.utils.exceptions import exception_handler_status500
from kanban_app.models import Board, Task, Comment
from kanban_app.api.serializers import BoardListSerializer, BoardDetailSerializer, TaskSerializer, TaskWriteSerializer, CommentSerializer, CommentCreateSerializer, BoardUpdateSerializer
from kanban_app.api.mixins import UserBoardsQuerysetMixin
from kanban_app.api.permissions import IsBoardOwnerOrMember


class BoardListCreateView(UserBoardsQuerysetMixin, generics.ListCreateAPIView):
    """Lists all boards or creates a new one"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardListSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return exception_handler_status500(exc, context=None)


class BoardDetailView(UserBoardsQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    """Reads, updates or deletes a board"""
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]
    serializer_class = BoardDetailSerializer

    def get_queryset(self):
        task_qs = (
            Task.objects
            .select_related("assignee", "reviewer", "board")
            .annotate(num_comments=Coalesce(Count("comments"), 0))
        )
        return (
            super()
            .get_queryset()
            .select_related("owner")
            .prefetch_related("members")
            .prefetch_related(Prefetch("tasks", queryset=task_qs))
        )
        
    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_object(self):
        board = super().get_object()
        self.check_object_permissions(self.request, board)
        return board

    def destroy(self, request, *args, **kwargs):
        try:
            board = self.get_object()
            board.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Board.DoesNotExist:
            return Response({"error": "Board nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return exception_handler_status500(exc, context=None)


class TasksAssignedToMeView(generics.ListAPIView):
    """Lists all tasks assigned to the current user"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        accessible_boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        return (Task.objects.filter(board__in=accessible_boards, assignee=user).select_related("board", "assignee", "reviewer"))


class TasksReviewedByMeView(generics.ListAPIView):
    """Lists all tasks reviewed by the current user"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        accessible_boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        return (Task.objects.filter(board__in=accessible_boards, reviewer=user).select_related("board", "assignee", "reviewer"))


class TasksInvolvedView(generics.ListAPIView):
    """Lists all tasks the current user is involved in"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        accessible_boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        return (
            Task.objects.filter(board__in=accessible_boards).filter(Q(assignee=user) | Q(reviewer=user)).select_related("board", "assignee", "reviewer"))


class TaskCreateView(generics.CreateAPIView):
    """Creates a new task"""
    queryset = Task.objects.all()
    serializer_class = TaskWriteSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

    def perform_create(self, serializer):
        board = serializer.validated_data["board"]
        self.check_object_permissions(self.request, board)
        serializer.save()

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            task = Task.objects.get(pk=response.data["id"])
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return exception_handler_status500(exc, context=None)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Lists, updates or deletes a task"""
    queryset = Task.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

    def get_object(self):
        task = super().get_object()
        self.check_object_permissions(self.request, task)
        return task

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return TaskWriteSerializer
        return TaskSerializer

    def patch(self, request, *args, **kwargs):
        try:
            kwargs["partial"] = True
            write_serializer = TaskWriteSerializer(
                self.get_object(),
                data=request.data,
                partial=True,
                context=self.get_serializer_context(),
            )
            write_serializer.is_valid(raise_exception=True)
            task = write_serializer.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
        except Exception as exc:
            return exception_handler_status500(exc, context=None)

    def put(self, request, *args, **kwargs):
        try:
            write_serializer = TaskWriteSerializer(self.get_object(), data=request.data, context=self.get_serializer_context(),)
            write_serializer.is_valid(raise_exception=True)
            task = write_serializer.save()
            return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
        except Exception as exc:
            return exception_handler_status500(exc, context=None)


class CommentsListCreateView(generics.ListCreateAPIView):
    """Lists or creates comments"""
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

    def get_task(self):
        return get_object_or_404(Task, pk=self.kwargs["task_id"])

    def get_queryset(self):
        task = self.get_task()
        self.check_object_permissions(self.request, task)
        return task.comments.select_related("author").order_by("created_at")

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CommentSerializer
        return CommentCreateSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["task"] = self.get_task()
        return ctx

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            return Response(CommentSerializer(obj).data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return exception_handler_status500(exc, context=None)


class CommentDeleteView(APIView):
    """Deletes a comment"""
    permission_classes = [permissions.IsAuthenticated, IsBoardOwnerOrMember]

    def delete(self, request, task_id: int, comment_id: int):
        try:
            task = get_object_or_404(Task, pk=task_id)
            self.check_object_permissions(request, task)

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
