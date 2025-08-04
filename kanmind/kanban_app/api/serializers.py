from rest_framework import serializers
from kanban_app.models import RegistrationUserModel


class RegistrationUserSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = RegistrationUserModel
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, data):
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "Passwörter stimmen nicht überein."})
        return data

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        user = RegistrationUserModel(
            fullname=validated_data["fullname"],
            email=validated_data["email"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
