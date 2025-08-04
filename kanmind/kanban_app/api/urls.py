from django.urls import path
from kanban_app.api.views import hello_world

urlpatterns = [
    path('', hello_world),
]