from django.urls import include, path
from rest_framework.routers import DefaultRouter

from payments_service.views import PaymentViewSet, RenewPaymentSessionView


router = DefaultRouter()
router.register("payments", PaymentViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "payments/<int:pk>/renew/",
        RenewPaymentSessionView.as_view(),
        name="renew_payment_session",
    ),
]

app_name = "payments"
