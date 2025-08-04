from django.db import models
from django.contrib.auth.hashers import make_password


class RegistrationUserModel(models.Model):
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # als Hash gespeichert

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def __str__(self):
        return f"{self.fullname}"