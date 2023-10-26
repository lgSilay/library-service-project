from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from books_service.serializers import BookDetailSerializer
from .models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book"
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.SlugRelatedField(slug_field="title", many=False, read_only=True)


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookDetailSerializer(many=False, read_only=True)


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
            raise serializers.ValidationError(f"Book '{book.title}' is out of stock")

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
