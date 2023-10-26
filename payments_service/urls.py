from django.urls import include, path
from rest_framework.routers import DefaultRouter

from payments_service.views import PaymentViewSet


router = DefaultRouter()
router.register("payments", PaymentViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "payments"
