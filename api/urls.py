from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import BookView, BookIdView


urlpatterns = [
    path("books/", csrf_exempt(BookView.as_view())),
    path("books/<int:book_id>", csrf_exempt(BookIdView.as_view())),
]
