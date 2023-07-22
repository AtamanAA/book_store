from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


from book.models import Book


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, through="OrderItem")
    status = models.CharField(max_length=128)
    created_at = models.DateTimeField(blank=True)
    invoice_id = models.CharField(max_length=200, null=True)
    pay_url = models.CharField(max_length=500, null=True)

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

        order_info = {
            "id": self.id,
            "user_id": self.user.id,
            "books": books,
            "status": self.status,
            "full_price": self.full_price,
            "created_at": self.created_at,
            "invoice_id": self.invoice_id,
            "pay_url": self.pay_url,
        }
        return order_info


class OrderItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True)
