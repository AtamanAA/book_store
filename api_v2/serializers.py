from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password, ValidationError
from rest_framework import serializers

from author.models import Author
from book.models import Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name", "patronymic", "birthday"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "name", "authors", "genre", "publication_date"]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, style={"input_type": "password", "placeholder": "Password"}
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return user

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value
