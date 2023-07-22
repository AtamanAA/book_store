from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password, ValidationError
from rest_framework import serializers

from author.models import Author
from book.models import Book
from order.models import Order


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name", "patronymic", "birthday"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "name",
            "authors",
            "genre",
            "publication_date",
            "price",
            "count",
        ]


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


class BooksOrderSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField()


class OrderSerializer(serializers.ModelSerializer):
    books = BooksOrderSerializer(many=True)
    user = UserSerializer(read_only=True)
    status = serializers.CharField(max_length=128, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "books"]


class MonoCallbackSerializer(serializers.Serializer):
    invoiceId = serializers.CharField()
    status = serializers.CharField()
    amount = serializers.IntegerField()
    ccy = serializers.IntegerField()
    reference = serializers.CharField()
