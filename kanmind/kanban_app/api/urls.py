from django.urls import path
from kanban_app.api.views import RegistrationUserView, EmailLoginView

urlpatterns = [
    path('login/', EmailLoginView.as_view(), name='login-user'),
    path('registration/', RegistrationUserView.as_view(), name='register-user'),
]