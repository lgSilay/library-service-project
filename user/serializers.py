from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class TelegramUserSerializer(serializers.ModelSerializer):
    """Update user telegram_id when logged in from telegram"""
    class Meta:
        model = get_user_model()
        fields = ("telegram_id",)


        def update(self, instance, validated_data):
            telegram_id = validated_data.pop("telegram_id", None)
            user = super().update(instance, validated_data)
            if telegram_id:
                user["telegram_id"] = telegram_id
                user.save()

            return user
