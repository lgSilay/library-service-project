from rest_framework import serializers

from books_service.models import Author, Book


class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title_image")


class AuthorImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "author_profile_image")
