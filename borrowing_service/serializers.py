from rest_framework import serializers

from books_service.serializers import BookDetailSerializer
from .models import Borrowing


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookDetailSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book"
        )
