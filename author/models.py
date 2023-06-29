from django.db import models


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    patronymic = models.CharField(blank=True, max_length=20)
    birthday = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.patronymic}"

    def __repr__(self):
        return f"Author(id={self.id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name} {self.patronymic}"
