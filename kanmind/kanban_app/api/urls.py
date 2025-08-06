from django.urls import path
from kanban_app.api.views import RegistrationUserView, EmailLoginView, BoardListCreateView, BoardDetailView, MailCheckView, TaskCreateView, TasksAssignedToMeView, TasksReviewedByMeView

urlpatterns = [
    path('login/', EmailLoginView.as_view(), name='login-user'),
    path('registration/', RegistrationUserView.as_view(), name='register-user'),
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('email-check/', MailCheckView.as_view(), name='email-check'),
    path("tasks/assigned-to-me/", TasksAssignedToMeView.as_view(), name="tasks-assigned"),
    path("tasks/reviewing/", TasksReviewedByMeView.as_view(), name="tasks-reviewing"),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
]