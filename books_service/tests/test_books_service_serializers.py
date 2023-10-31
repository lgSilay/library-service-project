from django.test import TestCase
from rest_framework.test import APIRequestFactory

from books_service.models import Author, Book
from books_service.serializers.common import (
    AuthorSerializer,
    BookSerializer,
    BookListSerializer,
    BookDetailSerializer,
)


class SerializerTests(TestCase):
    def setUp(self) -> None:
        self.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
            author_profile_image="path_to_image.jpg",
        )
        self.book = Book.objects.create(
            title="Sample Book",
            author=self.author,
            cover="hard",
            inventory=10,
            daily_fee=15.00,
        )

    def test_author_serializer(self) -> None:
        serializer = AuthorSerializer(self.author)
        data = serializer.data
        self.assertEqual(data["id"], self.author.id)
        self.assertEqual(data["first_name"], self.author.first_name)
        self.assertEqual(data["last_name"], self.author.last_name)
        self.assertEqual(data["full_name"], self.author.full_name)
        self.assertEqual(
            data["author_profile_image"], self.author.author_profile_image.url
        )

    def test_book_serializer(self) -> None:
        serializer = BookSerializer(self.book)
        data = serializer.data
        self.assertEqual(data["id"], self.book.id)
        self.assertEqual(data["title"], self.book.title)
        self.assertEqual(data["author"], self.book.author.id)
        self.assertEqual(data["cover"], self.book.cover)
        self.assertEqual(data["inventory"], self.book.inventory)
        self.assertEqual(
            data["daily_fee"], "{:.2f}".format(self.book.daily_fee)
        )

    def test_book_list_serializer(self) -> None:
        request = APIRequestFactory().get("/books/")
        serializer = BookListSerializer(
            self.book, context={"request": request}
        )
        data = serializer.data
        self.assertEqual(data["id"], self.book.id)
        self.assertEqual(data["title"], self.book.title)
        self.assertEqual(data["title_image"], self.book.title_image)
        self.assertEqual(data["author"], self.book.author.id)
        self.assertEqual(data["author_full_name"], self.book.author.full_name)
        self.assertEqual(data["cover"], self.book.cover)
        self.assertEqual(data["inventory"], self.book.inventory)
        self.assertTrue("book_link" in data)

    def test_book_detail_serializer(self) -> None:
        request = APIRequestFactory().get("/books/")
        serializer = BookDetailSerializer(
            self.book, context={"request": request}
        )
        data = serializer.data
        self.assertEqual(data["id"], self.book.id)
        self.assertEqual(data["title"], self.book.title)
        self.assertEqual(data["title_image"], self.book.title_image)
        self.assertEqual(data["author"], self.book.author.id)
        self.assertEqual(data["author_full_name"], self.book.author.full_name)
        self.assertTrue("author_link" in data)
        self.assertEqual(data["cover"], self.book.cover)
        self.assertEqual(data["inventory"], self.book.inventory)
        self.assertEqual(
            data["daily_fee"], "{:.2f}".format(self.book.daily_fee)
        )
