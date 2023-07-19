import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpRequest
from django.http import JsonResponse
from django.urls import reverse
from django.utils.cache import get_cache_key
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response

from author.models import Author
from book.models import Book
from order.models import Order, OrderItem, MonoSettings
from .permissions import UserPermissions
from .serializers import (
    AuthorSerializer,
    BookSerializer,
    UserSerializer,
    OrderSerializer,
    MonoCallbackSerializer,
)
from order.mono import verify_signature


class BookView(APIView):
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

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
            expire_view_cache(request, "all_books")
            return JsonResponse(book.get_info(), safe=False)
        return JsonResponse(serializer.errors, status=400)


class BookIdView(APIView):
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

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
                expire_view_cache(request, "all_books")
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
            expire_view_cache(request, "all_books")
            return JsonResponse(
                {"Success": f"Book with id={book_id} success delete"}, status=200
            )
        except Book.DoesNotExist:
            return JsonResponse(
                {"Error": f"Book with id={book_id} not found"}, status=404
            )


class AuthorView(APIView):
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

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
            expire_view_cache(request, "all_authors")
            return JsonResponse(serializer.data, safe=False)
        return JsonResponse(serializer.errors, status=400)


class AuthorIdView(APIView):
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

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
                expire_view_cache(request, "all_authors")
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
            expire_view_cache(request, "all_authors")
            return JsonResponse(
                {"Success": f"Author with id={author_id} success delete"}, status=200
            )
        except Author.DoesNotExist:
            return JsonResponse(
                {"Error": f"Author with id={author_id} not found"}, status=404
            )


def expire_view_cache(request, view_name, args=None, key_prefix=None):
    if request.get_host() == "testserver":
        request_meta = {"SERVER_NAME": "127.0.0.1", "SERVER_PORT": "8000"}
    else:
        request_meta = {
            "SERVER_NAME": request.META["SERVER_NAME"],
            "SERVER_PORT": request.META["SERVER_PORT"],
        }

    request = HttpRequest()
    request.META = request_meta
    request.path = reverse(view_name, args=args)

    if settings.USE_I18N:
        request.LANGUAGE_CODE = settings.LANGUAGE_CODE

    cache_key = get_cache_key(request, key_prefix=key_prefix)
    if cache_key:
        if cache_key in cache:
            cache.delete(cache_key)
            return True
        else:
            return False
    else:
        return False


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [
        UserPermissions,
    ]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by("-id")

    def create(self, request, *args, **kwargs):
        order = OrderSerializer(data=request.data)
        order.is_valid(raise_exception=True)
        # webhook_url = request.build_absolute_uri(reverse("mono_callback"))
        webhook_url = "url for pay"
        order_data = create_order(order.validated_data, webhook_url)
        return Response(order_data)


class OrderView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        orders = [order.get_info() for order in Order.objects.all().order_by("-id")]
        return Response(orders)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = Order(user=request.user, status="created")
            order.save()

            for row in serializer.data["books"]:
                book = Book.objects.get(pk=row["book_id"])
                quantity = row["quantity"]
                order_item = OrderItem(order=order, book=book, quantity=quantity)
                order_item.save()

            webhook_url = request.build_absolute_uri(reverse("mono_callback"))
            # webhook_url = "https://webhook.site/8690a212-49cf-46d4-a57e-5f3cf9c1af91"

            body = {
                "amount": order.full_price,
                "merchantPaymInfo": {
                    "reference": str(order.id),
                    "basketOrder": order.get_mono_basket_info(),
                },
                "webHookUrl": webhook_url,
            }
            r = requests.post(
                "https://api.monobank.ua/api/merchant/invoice/create",
                headers={"X-Token": settings.MONOBANK_API_KEY},
                json=body,
            )
            r.raise_for_status()
            order.invoice_id = r.json()["invoiceId"]
            order.save()
            url = r.json()["pageUrl"]

            response = {"order_id": order.id, "pageUrl": url}
            return Response(response)

        return JsonResponse(serializer.errors, status=400)


class OrderCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        public_key = MonoSettings.get_token()
        if not verify_signature(
            public_key, request.headers.get("X-Sign"), request.body
        ):
            return Response({"status": "signature mismatch"}, status=400)
        callback = MonoCallbackSerializer(data=request.data)
        callback.is_valid(raise_exception=True)
        try:
            order = Order.objects.get(id=callback.validated_data["reference"])
        except Order.DoesNotExist:
            return Response({"status": "order not found"}, status=404)
        if order.invoice_id != callback.validated_data["invoiceId"]:
            return Response({"status": "invoiceId mismatch"}, status=400)
        order.status = callback.validated_data["status"]
        order.save()
        return Response({"status": "ok"})


