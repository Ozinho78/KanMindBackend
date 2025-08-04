from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import RegistrationUserSerializer

class RegistrationUserView(generics.CreateAPIView):
    serializer_class = RegistrationUserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.save()
        return Response(user_data, status=status.HTTP_201_CREATED)
