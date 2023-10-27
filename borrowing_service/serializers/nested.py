from rest_framework import serializers

from borrowing_service.models import Borrowing


class BorrowingPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
