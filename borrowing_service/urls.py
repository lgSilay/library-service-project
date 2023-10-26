from django.urls import path, include
from rest_framework import routers

from .views import BorrowingViewSet


router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "borrowing_service"
