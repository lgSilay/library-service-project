from rest_framework import serializers
from django.urls import reverse

from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    books_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Author
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "books_count",
        )


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")


class BookListSerializer(BookSerializer):
    author_full_name = serializers.SlugRelatedField(
        source="author", read_only=True, slug_field="full_name"
    )
    book_link = serializers.HyperlinkedIdentityField(
        view_name="books_service:books-detail", read_only=True
    )

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "author_full_name",
            "cover",
            "inventory",
            "book_link",
        )


class BookDetailSerializer(BookListSerializer):
    author_link = serializers.HyperlinkedRelatedField(
        source="author",
        read_only=True,
        view_name="books_service:authors-detail",
    )

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "author_full_name",
            "author_link",
            "cover",
            "inventory",
            "daily_fee",
        )
