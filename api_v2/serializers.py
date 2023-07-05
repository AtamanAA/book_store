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
