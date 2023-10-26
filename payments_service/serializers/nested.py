from rest_framework import serializers

from payments_service.models import Payment


class PaymentBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "type",
            "status",
            "session_url",
            "session_id",
            "money_to_pay",
        )
