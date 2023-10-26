from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count

from .models import Author, Book
from .serializers import (
    BookSerializer,
    BookDetailSerializer,
    BookListSerializer,
    AuthorSerializer,
)
from .permissions import IsAdminOrReadOnly


class DefaultPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 1000


class BasePermissionPagination:
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = DefaultPagination


class AuthorViewSet(BasePermissionPagination, viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_queryset(self):
        return Author.objects.annotate(books_count=Count("books"))


class BookViewSet(BasePermissionPagination, viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        if self.action == "retrieve":
            return BookDetailSerializer
        return self.serializer_class
