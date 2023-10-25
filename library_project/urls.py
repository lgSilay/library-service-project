from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/borrowing_service/", include("borrowing_service.urls", namespace="borrowing_service")),
    path("api/books/", include("books_service.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/user/", include("user.urls", namespace="user")),
    path(
        "api/payments/", include("payments_service.urls", namespace="payments")
    ),
]
