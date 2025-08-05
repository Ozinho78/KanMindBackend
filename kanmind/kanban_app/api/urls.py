from django.urls import path
from kanban_app.api.views import RegistrationUserView, EmailLoginView, BoardListCreateView, BoardDetailView

urlpatterns = [
    path('login/', EmailLoginView.as_view(), name='login-user'),
    path('registration/', RegistrationUserView.as_view(), name='register-user'),
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
]