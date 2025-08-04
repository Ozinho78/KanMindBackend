from rest_framework import serializers
from django.contrib.auth.models import User
# from rest_framework.authtoken.models import Token
# import re


class RegistrationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        user = User(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
















# class RegistrationUserSerializer(serializers.ModelSerializer):
#     fullname = serializers.CharField(write_only=True)
#     repeated_password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ["fullname", "email", "password", "repeated_password"]
#         extra_kwargs = {
#             "password": {"write_only": True}
#         }

#     def validate_fullname(self, value):
#         if len(value.strip().split()) < 2:
#             raise serializers.ValidationError("Bitte Vor- und Nachname angeben.")
#         return value

#     def validate_email(self, value):
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("E-Mail-Adresse wird bereits verwendet.")
#         return value

#     def validate_password(self, value):
#         if len(value) < 8:
#             raise serializers.ValidationError("Passwort muss mindestens 8 Zeichen lang sein.")
#         if not re.search(r"[A-Z]", value):
#             raise serializers.ValidationError("Mindestens ein Großbuchstabe erforderlich.")
#         if not re.search(r"[a-z]", value):
#             raise serializers.ValidationError("Mindestens ein Kleinbuchstabe erforderlich.")
#         if not re.search(r"\d", value):
#             raise serializers.ValidationError("Mindestens eine Zahl erforderlich.")
#         if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
#             raise serializers.ValidationError("Mindestens ein Sonderzeichen erforderlich.")
#         return value

#     def validate(self, data):
#         if data["password"] != data["repeated_password"]:
#             raise serializers.ValidationError({"password": "Passwörter stimmen nicht überein."})
#         return data

#     def create(self, validated_data):
#         fullname = validated_data.pop("fullname")
#         validated_data.pop("repeated_password")

#         first_name, last_name = fullname.split(" ", 1)

#         user = User(
#             username=validated_data["email"],
#             email=validated_data["email"],
#             first_name=first_name,
#             last_name=last_name
#         )
#         user.set_password(validated_data["password"])
#         user.save()

#         token, created = Token.objects.get_or_create(user=user)

#         return {
#             "token": token.key,
#             "fullname": f"{first_name} {last_name}",
#             "email": user.email,
#             "user_id": user.id
#         }
