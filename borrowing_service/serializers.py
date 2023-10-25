from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from borrowing_service.models import Borrowing


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date"
        )
        read_only_fields = ("id", "borrow_date")

    def validate(self, attrs):
        book = attrs.get("book")
        if book.inventory < 1:
            raise serializers.ValidationError(
                f"Book '{book.title}' is out of stock."
            )

        expected_return_date = attrs.get("expected_return_date")
        borrow_date = attrs.get("borrow_date")
        actual_return_date = attrs.get("actual_return_date")
        Borrowing.validate_date(
            expected_return_date,
            borrow_date,
            actual_return_date,
            ValidationError,
        )
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data.get("book")
            borrowing = Borrowing.objects.create(**validated_data)
            book.inventory -= 1
            book.save()
            return borrowing
