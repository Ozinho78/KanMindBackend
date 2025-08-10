"""Contains registrations and login urls and an additional mail check with query params"""
from django.urls import path
from auth_app.api.views import RegistrationUserView, MailLoginView, MailCheckView


urlpatterns = [
    path("login/", MailLoginView.as_view(), name="login-user"),
    path("registration/", RegistrationUserView.as_view(), name="register-user"),
    path("email-check/", MailCheckView.as_view(), name="email-check"),
]
