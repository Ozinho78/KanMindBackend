from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegistrationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        account = User(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"]
        )
        account.set_password(validated_data["password"])
        account.save()
        return account


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            account = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "E-Mail-Adresse nicht gefunden."})

        account = authenticate(username=account.username, password=password)
        if not account:
            raise serializers.ValidationError({"password": "Falsches Passwort."})

        data["user"] = account
        return data
