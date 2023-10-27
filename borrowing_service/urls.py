from django.urls import path, include
from rest_framework import routers

from .views import BorrowingViewSet, ReturnBorrowingView


router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "borrowings/<int:pk>/return/",
        ReturnBorrowingView.as_view(),
        name="order_return",
    ),
]

app_name = "borrowing_service"
