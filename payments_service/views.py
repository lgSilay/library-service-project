from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from payments_service.models import Payment
from payments_service.serializers.common import (
    PaymentListSerializer,
    PaymentDetailSerializer,
)


class PaymentViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Payment.objects.select_related("borrowing__book")
    serializer_class = PaymentDetailSerializer

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        return self.serializer_class
