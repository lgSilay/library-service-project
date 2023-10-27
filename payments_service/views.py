from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework_simplejwt.views import status

from payments_service.models import Payment
from payments_service.serializers.common import (
    PaymentListSerializer,
    PaymentDetailSerializer,
)
from payments_service.permissions import IsOwnerOrAdmin


class PaymentViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Payment.objects.select_related("borrowing__book")
    serializer_class = PaymentDetailSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        return self.serializer_class

    @action(methods=["GET"], detail=False, url_path="success")
    def order_success(self, request):
        if session_id := request.query_params.get("session_id"):
            payment = Payment.objects.get(session_id=session_id)
            payment.status = "paid"
            payment.save()
            return Response(
                {"info": "Your payment was successful"},
                status=status.HTTP_200_OK,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET"], detail=False, url_path="cancel")
    def order_cancel(self, request):
        return Response(
            {
                "info": (
                    "Payment can be performed a bit later. "
                    "Session will be active for 24 hours."
                )
            },
            status=status.HTTP_200_OK,
        )
