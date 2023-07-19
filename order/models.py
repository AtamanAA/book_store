from datetime import datetime

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from book.models import Book


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, through="OrderItem")
    status = models.CharField(max_length=128)
    created_at = models.DateTimeField(default=datetime.now())
    invoice_id = models.CharField(max_length=200, null=True)

    @property
    def full_price(self):
        full_price = 0
        for item in OrderItem.objects.filter(order_id=self.id):
            full_price += Book.objects.get(pk=item.book_id).price * item.quantity
        return full_price

    def get_info(self):
        books = []
        for item in OrderItem.objects.filter(order_id=self.id):
            book = Book.objects.get(pk=item.book_id)
            books.append(
                {"book_id": book.id, "book_name": book.name, "quantity": item.quantity}
            )

        book_info = {
            "id": self.id,
            "user_id": self.user.id,
            "books": books,
            "status": self.status,
            "full_price": self.full_price,
            "created_at": self.created_at,
        }
        return book_info

    def get_mono_basket_info(self):
        basket = []
        for item in OrderItem.objects.filter(order_id=self.id):
            book = Book.objects.get(pk=item.book_id)
            basket.append(
                {
                    "name": book.name,
                    "qty": item.quantity,
                    "sum": book.price * item.quantity,
                    "unit": "шт.",
                }
            )
        return basket


class OrderItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class MonoSettings(models.Model):
    public_key = models.CharField(max_length=1000)

    @classmethod
    def get_token(cls):
        # try:
        #     return cls.objects.last().public_key
        # except AttributeError:
        #     key = requests.get(
        #         "https://api.monobank.ua/api/merchant/pubkey",
        #         headers={"X-Token": settings.MONOBANK_API_KEY},
        #     ).json()["key"]
        #     cls.objects.create(public_key=key)
        #     return key

        key = requests.get(
            "https://api.monobank.ua/api/merchant/pubkey",
            headers={"X-Token": settings.MONOBANK_API_KEY},
        ).json()["key"]
        cls.objects.create(public_key=key)
        return key
