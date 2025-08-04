from django.urls import path
from kanban_app.api.views import RegistrationUserView

urlpatterns = [
    # path('login/', login_view, name='login'),
    path('registration/', RegistrationUserView.as_view(), name='register-user'),
]