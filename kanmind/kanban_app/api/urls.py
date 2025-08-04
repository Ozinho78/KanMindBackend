from django.urls import path
from kanban_app.api.views import hello_world, RegistrationUserModel

urlpatterns = [
    path('', hello_world),
    # path('login/', login_view, name='login'),
    path('registration/', RegistrationUserModel, name='register-user'),
]