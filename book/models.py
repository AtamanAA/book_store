from django.db import models

from author.models import Author


class Book(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    authors = models.ManyToManyField(Author, null=True, related_name="book")
    genre = models.CharField(max_length=40)
    publication_date = models.DateField()
    price = models.PositiveIntegerField(default=1000)
    count = models.IntegerField(default=0)

    # @staticmethod
    def get_info(self):
        authors = [author.get_full_name() for author in self.authors.select_related()]
        book_info = {
            "id": self.id,
            "name": self.name,
            "authors": authors,
            "genre": self.genre,
            "publication_date": self.publication_date,
            "count": self.count,
            "price": self.price,
        }
        return book_info
