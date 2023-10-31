from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.db.models import Count


from books_service.models import Author, Book
from books_service.serializers.common import (
    BookSerializer,
    AuthorSerializer,
)

AUTHOR_URL = reverse("books_service:authors-list")
BOOK_URL = reverse("books_service:books-list")


class AuthorViewSetTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@gmail.com", password="testpassword", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.author1 = Author.objects.create(
            first_name="John",
            last_name="Doe",
        )

    def test_author_list(self) -> None:
        response = self.client.get(AUTHOR_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_detail(self) -> None:
        response = self.client.get(
            reverse("books_service:authors-detail", args=[self.author1.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_creation(self) -> None:
        data = {"first_name": "Test", "last_name": "Tset"}
        response = self.client.post(AUTHOR_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_author_update(self) -> None:
        data = {
            "first_name": "Updated First Name",
            "last_name": "Updated Last Name",
        }
        response = self.client.patch(
            reverse("books_service:authors-detail", args=[self.author1.id]),
            data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_delete(self) -> None:
        response = self.client.delete(
            reverse("books_service:authors-detail", args=[self.author1.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_author_filter_by_books_count(self) -> None:
        response = self.client.get(AUTHOR_URL, {"books-count": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        authors = Author.objects.annotate(books_count=Count("books")).filter(
            books_count=2
        )
        serialized_authors = AuthorSerializer(authors, many=True)
        self.assertEqual(response.data["results"], serialized_authors.data)

    def test_author_filter_by_books_gt(self) -> None:
        response = self.client.get(AUTHOR_URL, {"books-gt": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        authors = Author.objects.annotate(books_count=Count("books")).filter(
            books_count__gt=5
        )
        serialized_authors = AuthorSerializer(authors, many=True)
        self.assertEqual(response.data["results"], serialized_authors.data)

    def test_author_filter_by_books_lt(self) -> None:
        response = self.client.get(AUTHOR_URL, {"books-lt": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        authors = Author.objects.annotate(books_count=Count("books")).filter(
            books_count__lt=3
        )
        serialized_authors = AuthorSerializer(authors, many=True)
        self.assertEqual(response.data["results"], serialized_authors.data)

    def test_author_filter_by_first_name(self) -> None:
        response = self.client.get(AUTHOR_URL, {"first-name": "John"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        authors = Author.objects.annotate(books_count=Count("books")).filter(
            first_name__icontains="John"
        )
        serialized_authors = AuthorSerializer(authors, many=True)
        self.assertEqual(response.data["results"], serialized_authors.data)

    def test_author_filter_by_last_name(self) -> None:
        response = self.client.get(AUTHOR_URL, {"last-name": "Johnson"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        authors = Author.objects.annotate(books_count=Count("books")).filter(
            last_name__icontains="Johnson"
        )
        serialized_authors = AuthorSerializer(authors, many=True)
        self.assertEqual(response.data["results"], serialized_authors.data)

    def test_author_filter_by_no_books(self) -> None:
        response = self.client.get(AUTHOR_URL, {"no-books": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        authors = Author.objects.annotate(books_count=Count("books")).exclude(
            books_count__gt=0
        )
        serialized_authors = AuthorSerializer(authors, many=True)
        self.assertEqual(response.data["results"], serialized_authors.data)

    def test_author_filter_by_has_books(self) -> None:
        response = self.client.get(AUTHOR_URL, {"has-books": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        authors = Author.objects.annotate(books_count=Count("books")).filter(
            books_count__gt=0
        )
        serialized_authors = AuthorSerializer(authors, many=True)
        self.assertEqual(response.data["results"], serialized_authors.data)


class BookViewSetTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@gmail.com", password="testpassword", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.author1 = Author.objects.create(
            first_name="John", last_name="Doe"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author=self.author1,
            cover="hard",
            inventory=5,
            daily_fee=15.00,
        )

    def test_book_list(self) -> None:
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_detail(self) -> None:
        response = self.client.get(
            reverse("books_service:books-detail", args=[self.book.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_creation(self) -> None:
        data = {
            "title": "New Book",
            "author": self.author1.id,
            "cover": "soft",
            "inventory": 10,
            "daily_fee": "10.00",
        }
        response = self.client.post(BOOK_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_book_update(self) -> None:
        data = {
            "title": "Updated Book Title",
            "cover": "soft",
            "inventory": 7,
            "daily_fee": "12.50",
        }
        response = self.client.patch(
            reverse("books_service:books-detail", args=[self.book.id]), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_delete(self) -> None:
        response = self.client.delete(
            reverse("books_service:books-detail", args=[self.book.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_book_filter_by_title(self) -> None:
        response = self.client.get(BOOK_URL, {"title": "New Book"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = Book.objects.filter(title__icontains="New Book")
        serialized_books = BookSerializer(books, many=True)
        self.assertEqual(response.data["results"], serialized_books.data)

    def test_book_filter_by_cover(self) -> None:
        response = self.client.get(BOOK_URL, {"cover": "soft"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = Book.objects.filter(cover__icontains="soft")
        serialized_books = BookSerializer(books, many=True)
        self.assertEqual(response.data["results"], serialized_books.data)

    def test_book_filter_by_unavailable(self) -> None:
        response = self.client.get(BOOK_URL, {"unavailable": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = Book.objects.filter(inventory=0)
        serialized_books = BookSerializer(books, many=True)
        self.assertEqual(response.data["results"], serialized_books.data)
