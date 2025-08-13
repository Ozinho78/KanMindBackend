from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from core.utils.validators import validate_email_format, validate_email_unique, validate_fullname, validate_password_strength
from auth_app.models import RegistrationUserModel


class RegistrationUserSerializer(serializers.ModelSerializer):
    """Serializes and validates user registration data"""
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "repeated_password", "fullname", "first_name", "last_name"]
        extra_kwargs = {
            "password": {"write_only": True},
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate_email(self, value: str) -> str:
        email = (value or "").strip()
        validate_email_format(email)
        validate_email_unique(email)
        return email

    def validate_fullname(self, value: str) -> str:
        fullname = (value or "").strip()
        validate_fullname(fullname)
        return fullname

    def validate(self, attrs: dict) -> dict:
        password = attrs.get("password") or ""
        repeated = attrs.get("repeated_password") or ""
        if password != repeated:
            raise serializers.ValidationError({"password": "Passwörter stimmen nicht überein."})
        validate_password_strength(password)
        return attrs

    def create(self, validated_data: dict) -> User:
        fullname = validated_data.pop("fullname").strip()
        validated_data.pop("repeated_password", None)
        first_name, last_name = fullname.split(" ", 1)
        email = validated_data["email"].strip().lower()
        user = User(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(validated_data["password"])
        user.save()
        RegistrationUserModel.objects.create(user=user, fullname=fullname)
        return user


class MailLoginSerializer(serializers.Serializer):
    """Serializes and validates login data"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""
        validate_email_format(email)
        try:
            account = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "E-Mail-Adresse nicht gefunden."})
        account = authenticate(username=account.username, password=password)
        if not account:
            raise serializers.ValidationError({"password": "Falsches Passwort."})
        data["user"] = account
        return data