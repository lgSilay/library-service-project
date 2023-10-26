from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from books_service.models import Book

from books_service.serializers import BookDetailSerializer
from payments_service.serializers.nested import PaymentBorrowingSerializer
from borrowing_service.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(
        slug_field="title", many=False, read_only=True
    )
    payments = PaymentBorrowingSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "payments",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookDetailSerializer(many=False, read_only=True)
    payments = PaymentBorrowingSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "payments",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.select_related("author")
    )

    class Meta:
        model = Borrowing
        fields = ("id", "book", "borrow_date", "expected_return_date")
        read_only_fields = ("id", "borrow_date")

    def validate(self, attrs):
        book = attrs.get("book")
        if book.inventory < 1:
            raise serializers.ValidationError(
                f"Book '{book.title}' is out of stock"
            )

        expected_return_date = attrs.get("expected_return_date")
        actual_return_date = attrs.get("actual_return_date")
        Borrowing.validate_date(
            expected_return_date,
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
