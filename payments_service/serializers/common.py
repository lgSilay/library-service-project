from rest_framework import serializers

from payments_service.models import Payment
from borrowing_service.serializers.nested import BorrowingPaymentSerializer


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing = BorrowingPaymentSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "type",
            "status",
            "borrowing",
            "session_url",
            "money_to_pay",
        )


class PaymentListSerializer(serializers.ModelSerializer):
    borrowing = serializers.CharField(
        source="borrowing.book.title", read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "type",
            "status",
            "borrowing",
            "session_url",
            "money_to_pay",
        )
