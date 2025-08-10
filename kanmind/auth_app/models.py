from django.contrib.auth.models import User
from django.db import models


class RegistrationUserModel(models.Model):
    """Model for user registration"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100)

    def __str__(self):
        return self.fullname