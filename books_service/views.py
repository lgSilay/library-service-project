from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from django.db.models import Count

from .models import Author, Book
from .serializers import (
    BookSerializer,
    BookDetailSerializer,
    BookListSerializer,
    AuthorSerializer,
)
from .permissions import IsAdminOrReadOnly


class BasePermission:
    permission_classes = (IsAdminOrReadOnly,)


class AuthorViewSet(BasePermission, viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def get_queryset(self):
        queryset = Author.objects.annotate(books_count=Count("books"))
        filters = {}

        filter_mapping = {
            "books-count": "books_count",
            "books-gt": "books_count__gt",
            "books-lt": "books_count__lt",
            "first-name": "first_name__icontains",
            "last-name": "last_name__icontains",
        }

        for param, filter_condition in filter_mapping.items():
            value = self.request.query_params.get(param)
            if value:
                filters[filter_condition] = value

        queryset = queryset.filter(**filters)

        if "no-books" in self.request.query_params:
            queryset = queryset.exclude(books_count__gt=0)
        if "has-books" in self.request.query_params:
            queryset = queryset.filter(books_count__gt=0)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="books-count",
                type=int,
                description=(
                    "Filter by books_count equal to a "
                    "specific number (e.g., ?books-count=50)"
                ),
            ),
            OpenApiParameter(
                name="books-gt",
                type=int,
                description=(
                    "Filter by authors with books_count greater "
                    "than a specific number (e.g., ?books-gt=50)"
                ),
            ),
            OpenApiParameter(
                name="books-lt",
                type=int,
                description=(
                    "Filter by authors with books_count "
                    "less than a specific number (e.g., ?books-lt=50)"
                ),
            ),
            OpenApiParameter(
                name="first-name",
                type=str,
                description=(
                        "Filter by author's first name (case-insensitive "
                        "partial match) (e.g., ?first-name=John)."
                ),
            ),
            OpenApiParameter(
                name="last-name",
                type=str,
                description=(
                        "Filter by author's last name (case-insensitive "
                        "partial match) (e.g., ?last-name=Johnson)."
                ),
            ),
            OpenApiParameter(
                name="no-books",
                type=str,
                description=(
                        "Filter authors with no books (e.g., ?no-books)"
                ),
            ),
            OpenApiParameter(
                name="has-books",
                type=str,
                description=(
                    "Filter authors with one or "
                    "more books (e.g., ?has-books)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BookViewSet(BasePermission, viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer

        if self.action == "retrieve":
            return BookDetailSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        title = self.request.query_params.get("title")
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type={"type": "str"},
                description="Filter by title fragment (ex. ?title=harry)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
