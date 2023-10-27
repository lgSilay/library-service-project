from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count

from .models import Author, Book
from .serializers.common import (
    BookSerializer,
    BookDetailSerializer,
    BookListSerializer,
    AuthorSerializer,
)
from .serializers.nested import AuthorImageSerializer, BookImageSerializer
from .permissions import IsAdminOrReadOnly


class CommonLogicMixin:
    permission_classes = (IsAdminOrReadOnly,)

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific crew member"""
        book_object = self.get_object()
        serializer = self.get_serializer(book_object, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorViewSet(CommonLogicMixin, viewsets.ModelViewSet):
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
            if value := self.request.query_params.get(param):
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
                description="Filter authors with no books (e.g., ?no-books)",
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

    def get_serializer_class(self):
        if self.action == "upload_image":
            return AuthorImageSerializer

        return self.serializer_class


class BookViewSet(CommonLogicMixin, viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer

        if self.action == "retrieve":
            return BookDetailSerializer

        if self.action == "upload_image":
            return BookImageSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset
        filters = {}

        filter_mapping = {
            "title": "title__icontains",
            "author-id": "author__id",
            "author-first-name": "author__first_name__icontains",
            "author-last-name": "author__last_name__icontains",
            "cover": "cover__icontains",
        }

        for param, filter_condition in filter_mapping.items():
            if value := self.request.query_params.get(param):
                filters[filter_condition] = value

        queryset = queryset.filter(**filters)

        if "available" in self.request.query_params:
            queryset = queryset.filter(inventory__gt=0)
        if "unavailable" in self.request.query_params:
            queryset = queryset.filter(inventory=0)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                type=str,
                description=(
                    "Filter by book title (case-insensitive "
                    "partial match) (e.g., ?title=example)."
                ),
            ),
            OpenApiParameter(
                name="author-id",
                type=int,
                description="Filter by author's ID (e.g., ?author-id=123).",
            ),
            OpenApiParameter(
                name="author-first-name",
                type=str,
                description=(
                    "Filter by author's first name (case-insensitive "
                    "partial match) (e.g., ?author-first-name=John)."
                ),
            ),
            OpenApiParameter(
                name="author-last-name",
                type=str,
                description=(
                    "Filter by author's last name (case-insensitive "
                    "partial match) (e.g., ?author-last-name=Johnson)."
                ),
            ),
            OpenApiParameter(
                name="cover",
                type=str,
                description=(
                    "Filter by book cover (case-insensitive "
                    "partial match) (e.g., ?cover=example)."
                ),
            ),
            OpenApiParameter(
                name="available",
                type=str,
                description="Filter available books (e.g., ?available).",
            ),
            OpenApiParameter(
                name="unavailable",
                type=str,
                description="Filter unavailable books (e.g., ?unavailable).",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
