from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, permissions
from kanban_app.api.serializers import RegistrationUserSerializer
from kanban_app.models import RegistrationUserModel


class RegistrationUserView(generics.CreateAPIView):
    queryset = RegistrationUserModel.objects.all()
    serializer_class = RegistrationUserSerializer
    permission_classes = [permissions.AllowAny]



















@api_view()
def hello_world(request):
    return Response({"message": "Hello, world!"})
