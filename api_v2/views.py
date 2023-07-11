from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView

from author.models import Author
from book.models import Book
from .serializers import AuthorSerializer, BookSerializer


class BookView(APIView):
    @method_decorator(cache_page(60 * 5))
    def get(self, request):
        try:
            optional_parameters = ["name", "genre", "authors"]
            filters = {}
            for key, value in request.GET.items():
                if key in optional_parameters:
                    if value:
                        filters[key] = value
                else:
                    return JsonResponse(
                        {"Error": "Invalid query parameter name"}, status=400
                    )
            books = [book.get_info() for book in Book.objects.filter(**filters)]
            return JsonResponse(books, safe=False)
        except ValueError:
            return JsonResponse(
                {"Error": "Invalid authors query parameter"}, status=400
            )

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            book = Book.objects.get(id=serializer.data["id"])
            return JsonResponse(book.get_info(), safe=False)
        return JsonResponse(serializer.errors, status=400)


class BookIdView(APIView):
    def get(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            return JsonResponse(book.get_info(), safe=False)
        except Book.DoesNotExist:
            return JsonResponse(
                {"Error": f"Book with id={book_id} not found"}, status=404
            )

    def put(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            serializer = BookSerializer(book, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(book.get_info(), safe=False)
            return JsonResponse(serializer.errors, status=400)
        except Book.DoesNotExist:
            return JsonResponse(
                {"Error": f"Book with id={book_id} not found"}, status=404
            )

    def delete(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            book.delete()
            return JsonResponse(
                {"Success": f"Book with id={book_id} success delete"}, status=200
            )
        except Book.DoesNotExist:
            return JsonResponse(
                {"Error": f"Book with id={book_id} not found"}, status=404
            )


class AuthorView(APIView):
    @method_decorator(cache_page(60 * 5))
    def get(self, request):
        optional_parameters = ["first_name"]
        filters = {}
        for key, value in request.GET.items():
            if key in optional_parameters:
                if value:
                    filters[key] = value
            else:
                return JsonResponse(
                    {"Error": "Invalid query parameter name"}, status=400
                )
        authors = Author.objects.filter(**filters)
        serializer = AuthorSerializer(authors, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False)
        return JsonResponse(serializer.errors, status=400)


class AuthorIdView(APIView):
    def get(self, request, author_id):
        try:
            author = Author.objects.get(id=author_id)
            serializer = AuthorSerializer(author)
            return JsonResponse(serializer.data, safe=False)
        except Author.DoesNotExist:
            return JsonResponse(
                {"Error": f"Author with id={author_id} not found"}, status=404
            )

    def put(self, request, author_id):
        try:
            author = Author.objects.get(id=author_id)
            serializer = AuthorSerializer(author, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, safe=False)
            return JsonResponse(serializer.errors, status=400)
        except Author.DoesNotExist:
            return JsonResponse(
                {"Error": f"Author with id={author_id} not found"}, status=404
            )

    def delete(self, request, author_id):
        try:
            author = Author.objects.get(id=author_id)
            author.delete()
            return JsonResponse(
                {"Success": f"Author with id={author_id} success delete"}, status=200
            )
        except Author.DoesNotExist:
            return JsonResponse(
                {"Error": f"Author with id={author_id} not found"}, status=404
            )
