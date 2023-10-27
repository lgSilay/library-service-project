from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from user.views import ManageUserView, CreateUserView, TelegramUserView, CustomTokenObtainPairView

urlpatterns = [
    path("register/", CreateUserView.as_view({"post": "create"}), name="create"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("me/", ManageUserView.as_view({"put": "update", "get": "retrieve", "patch": "update"}), name="manage"),
    path(
        "telegram/",
        TelegramUserView.as_view(
            {"patch": "partial_update", "get": "retrieve"}
        ),
        name="telegram",
    ),
]

app_name = "user"
