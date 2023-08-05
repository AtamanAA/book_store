from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    AuthorViewSet,
    UserViewSet,
    OrderView,
    OrderIdView,
    OrderCallbackView,
)


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"authors", AuthorViewSet, basename="author")
router.register(r"books", BookViewSet, basename="book")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("", include(router.urls)),
    path("orders/", csrf_exempt(OrderView.as_view()), name="all_orders"),
    path("orders/<int:order_id>/", csrf_exempt(OrderIdView.as_view())),
    path("monobank/callback", OrderCallbackView.as_view(), name="mono_callback"),
]
