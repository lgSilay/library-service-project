from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from payments_service.models import Payment
from payments_service.serializers import PaymentListSerializer, PaymentDetailSerializer


class PaymentViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentDetailSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        return self.serializer_class
