from django.contrib.auth.models import User
from django.db import models


class RegistrationUserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255)

    def __str__(self):
        return self.fullname