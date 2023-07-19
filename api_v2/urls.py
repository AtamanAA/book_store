from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.routers import DefaultRouter

from .views import (
    BookView,
    BookIdView,
    AuthorView,
    AuthorIdView,
    UserViewSet,
    OrderViewSet,
    OrderView,
    OrderCallbackView,
)


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("books/", csrf_exempt(BookView.as_view()), name="all_books"),
    path("books/<int:book_id>/", csrf_exempt(BookIdView.as_view())),
    path("authors/", csrf_exempt(AuthorView.as_view()), name="all_authors"),
    path("authors/<int:author_id>/", csrf_exempt(AuthorIdView.as_view())),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("", include(router.urls)),
    path("order/", csrf_exempt(OrderView.as_view()), name="all_orders"),
    path("monobank/callback", OrderCallbackView.as_view(), name="mono_callback"),
]
