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
    book = serializers.StringRelatedField(slug_field="title", many=False, read_only=True)


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookDetailSerializer(many=False, read_only=True)
