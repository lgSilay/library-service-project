from rest_framework import serializers
from borrowing_service.serializers import BorrowingDetailSerializer

from payments_service.models import Payment


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing = BorrowingDetailSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "type",
            "status",
            "borrowing",
            "session_url",
            "session_id",
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
            "session_id",
            "money_to_pay",
        )
