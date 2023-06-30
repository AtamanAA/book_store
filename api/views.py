from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import JsonResponse
from django.views import View
import json

from book.models import Book
from author.models import Author


class BookView(View):
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
        try:
            request_body = json.loads(request.body)
        except ValueError:
            return JsonResponse({"Error": "Invalid json"}, status=400)

        name = request_body.get("name")
        authors = request_body.get("authors")
        genre = request_body.get("genre")
        publication_date = request_body.get("publication_date")

        for param in request_body:
            if not param:
                return JsonResponse({"Error": "Missing data fields"}, status=400)

        try:
            if len(name) > 128:
                return JsonResponse({"Error": "Name field is too long"}, status=400)
            if len(genre) > 40:
                return JsonResponse({"Error": "Genre field is too long"}, status=400)

            book = Book(name=name, genre=genre, publication_date=publication_date)
            book.save()

            if not isinstance(authors, int):
                for author in authors:
                    book.authors.add(author)
            else:
                book.authors.add(authors)

            return JsonResponse(book.get_info(), safe=False)

        except ValueError:
            return JsonResponse({"Error": "Invalid authors field"}, status=400)
        except TypeError:
            return JsonResponse({"Error": "Invalid fields name"}, status=400)
        except ValidationError:
            return JsonResponse({"Error": "Invalid publication_date field"}, status=400)
        except IntegrityError:
            return JsonResponse({"Error": "Authors doesn't found"}, status=400)


class BookIdView(View):
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
            request_body = json.loads(request.body)
        except ValueError:
            return JsonResponse({"Error": "Invalid json"}, status=400)

        try:
            book = Book.objects.get(id=book_id)
            authors = request_body.get("authors")
            if authors:
                book.authors.clear()
            if not isinstance(authors, int):
                for author in authors:
                    book.authors.add(author)
            else:
                book.authors.add(authors)

            optional_parameters = ["name", "genre", "publication_date"]
            update_param = {}
            for key, value in request_body.items():
                if key in optional_parameters:
                    if value:
                        update_param[key] = value
                    else:
                        return JsonResponse(
                            {"Error": "Missing data fields"}, status=400
                        )

            if len(update_param["name"]) > 128:
                return JsonResponse({"Error": "Name field is too long"}, status=400)
            if len(update_param["genre"]) > 40:
                return JsonResponse({"Error": "Genre field is too long"}, status=400)

            Book.objects.filter(pk=book_id).update(**update_param)

            book_new = Book.objects.get(id=book_id)

            return JsonResponse(book_new.get_info(), safe=False)
        except Book.DoesNotExist:
            return JsonResponse(
                {"Error": f"Book with id={book_id} not found"}, status=404
            )
        except ValueError:
            return JsonResponse({"Error": "Invalid authors field"}, status=400)
        except TypeError:
            return JsonResponse({"Error": "Invalid fields name"}, status=400)
        except ValidationError:
            return JsonResponse({"Error": "Invalid publication_date field"}, status=400)
        except IntegrityError:
            return JsonResponse({"Error": "Authors doesn't found"}, status=400)

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


class AuthorView(View):
    def get(self, request):
        try:
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
            authors = list(Author.objects.filter(**filters).values())
            return JsonResponse(authors, safe=False)
        except ():
            pass


class AuthorIdView(View):
    def get(self, request, author_id):
        try:
            Author.objects.get(id=author_id)
            author = list(Author.objects.filter(id=author_id).values())[0]
            return JsonResponse(author, safe=False)
        except Author.DoesNotExist:
            return JsonResponse(
                {"Error": f"Author with id={author_id} not found"}, status=404
            )
