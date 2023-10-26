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
        return Author.objects.annotate(books_count=Count("books"))


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
                description="Filter by title fragment (ex. ?title=harry)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
