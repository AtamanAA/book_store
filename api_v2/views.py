from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .permissions import UserPermissions
from .serializers import (
    AuthorSerializer,
    BookSerializer,
    UserSerializer,
    OrderSerializer,
    MonoCallbackSerializer,
)
from author.models import Author
from book.models import Book
from order.models import Order, OrderItem
from order.mono import verify_signature, create_mono_order, get_mono_token


@method_decorator(cache_page(60 * 5), name="list")
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["name", "genre", "authors"]
    ordering_fields = ["publication_date"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            books = []
            for item in serializer.data:
                book = Book.objects.get(id=item["id"])
                books.append(book.get_info())
            return self.get_paginated_response(books)

        serializer = self.get_serializer(queryset, many=True)
        books = []
        for item in serializer.data:
            book = Book.objects.get(id=item["id"])
            books.append(book.get_info())
        return Response(books)

    def retrieve(self, request, *args, **kwargs):
        book = self.get_object()
        return Response(book.get_info())

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        book = Book.objects.get(pk=serializer.data["id"])
        return Response(
            book.get_info(), status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        book = self.get_object()
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(book.get_info(), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(cache_page(60 * 5), name="list")
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ["first_name"]

    def update(self, request, *args, **kwargs):
        author = self.get_object()
        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [
        UserPermissions,
    ]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = None


class OrderView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        orders = [order.get_info() for order in Order.objects.all().order_by("-id")]
        return Response(orders)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = Order(
                user=request.user, status="created", created_at=timezone.now()
            )
            order.save()

            if serializer.data["books"]:
                for row in serializer.data["books"]:
                    book_id = row["book_id"]
                    try:
                        book = Book.objects.get(pk=book_id)
                    except Book.DoesNotExist:
                        order.delete()
                        return Response(
                            {"Error": f"Book with id {book_id} not found"},
                            status=status.HTTP_404_NOT_FOUND,
                        )
                    quantity = row["quantity"]
                    if book.count < quantity:
                        order.delete()
                        return Response(
                            {
                                "Error": f"There are not enough books with id {book_id} in stock to create an order"
                            },
                            status=status.HTTP_406_NOT_ACCEPTABLE,
                        )
                    if quantity > 0:
                        order_item = OrderItem(
                            order=order, book=book, quantity=quantity
                        )
                        order_item.save()
                    else:
                        order.delete()
                        return Response(
                            {"Error": "Quantity must be more that 0"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                webhook_url = request.build_absolute_uri(reverse("mono_callback"))
                response = create_mono_order(order, webhook_url)
                return Response(response)
            else:
                order.delete()
                return Response(
                    {"books": ["This field is required."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return JsonResponse(serializer.errors, status=400)


class OrderIdView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            return JsonResponse(order.get_info(), safe=False)
        except Order.DoesNotExist:
            return JsonResponse(
                {"Error": f"Order with id={order_id} not found"}, status=404
            )

    def delete(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            order.delete()
            return JsonResponse(
                {"Success": f"Order with id={order_id} success delete"}, status=200
            )
        except Order.DoesNotExist:
            return JsonResponse(
                {"Error": f"Order with id={order_id} not found"}, status=404
            )


class OrderCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        public_key = get_mono_token()
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
        callback_status = callback.validated_data["status"]
        if callback_status == "success" and order.status != "success":
            for item in OrderItem.objects.filter(order_id=order.id):
                book = Book.objects.get(pk=item.book_id)
                book.count -= 1
                book.save()
        order.status = callback_status
        order.save()
        return Response({"status": "ok"})
