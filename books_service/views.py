from rest_framework import viewsets
from django.db.models import Count

from .models import Author, Book
from .serializers import (
    BookSerializer,
    BookDetailSerializer,
    BookListSerializer,
    AuthorSerializer,
)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_queryset(self):
        return Author.objects.annotate(books_count=Count("books"))


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        if self.action == "retrieve":
            return BookDetailSerializer
        return self.serializer_class
