"""Contains all endpoints after login/registration"""
from django.urls import path
from kanban_app.api.views import BoardListCreateView, BoardDetailView, TaskCreateView, TasksAssignedToMeView, TasksReviewedByMeView, TaskDetailView, TasksInvolvedView, CommentsListCreateView, CommentDeleteView


urlpatterns = [
    path("boards/", BoardListCreateView.as_view(), name='board-list-create'),
    path("boards/<int:pk>/", BoardDetailView.as_view(), name='board-detail'),
    path("tasks/assigned-to-me/", TasksAssignedToMeView.as_view(), name="tasks-assigned"),
    path("tasks/reviewing/", TasksReviewedByMeView.as_view(), name="tasks-reviewing"),
    path("tasks/involved/", TasksInvolvedView.as_view(), name="tasks-involved"),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path('tasks/<int:task_id>/comments/', CommentsListCreateView.as_view(), name='comments-list-create'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', CommentDeleteView.as_view(), name='comment-delete'),
]