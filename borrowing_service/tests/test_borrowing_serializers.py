from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from books_service.models import Book, Author
from borrowing_service.models import Borrowing
from borrowing_service.serializers import (
    BorrowingCreateSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)


class BorrowingSerializerTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test123",
            first_name="test_first",
            last_name="test_last",
        )
        self.author = Author.objects.create(
            first_name="Test",
            last_name="Author",
        )
        self.book = Book.objects.create(
            title="Test_Book",
            author=self.author,
            cover="hard",
            inventory=4,
            daily_fee=150.00,
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date()
            + timezone.timedelta(days=7),
            book=self.book,
            user=self.user,
        )

    def test_borrowing_create_serializer_valid(self) -> None:
        data = {
            "book": self.book.id,
            "borrow_date": timezone.now().date(),
            "expected_return_date": timezone.now().date()
            + timezone.timedelta(days=7),
        }
        serializer = BorrowingCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_borrowing_create_serializer_invalid_out_of_stock(self) -> None:
        self.book.inventory = 0
        self.book.save()
        data = {
            "book": self.book.id,
            "borrow_date": timezone.now().date(),
            "expected_return_date": timezone.now().date()
            + timezone.timedelta(days=7),
        }
        serializer = BorrowingCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "Book 'Test_Book' is out of stock",
            serializer.errors["non_field_errors"],
        )

    def test_borrowing_create_serializer_invalid_dates(self) -> None:
        data = {
            "book": self.book.id,
            "borrow_date": timezone.now().date(),
            "expected_return_date": timezone.now().date()
            - timezone.timedelta(days=1),
        }
        serializer = BorrowingCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "Expected return date must be later than Borrow date",
            serializer.errors["expected_return_date"],
        )

    def test_borrowing_list_serializer(self) -> None:
        serializer = BorrowingListSerializer(self.borrowing)
        data = serializer.data
        self.assertEqual(data["id"], self.borrowing.id)
        self.assertEqual(data["borrow_date"], str(self.borrowing.borrow_date))
        self.assertEqual(
            data["expected_return_date"],
            str(self.borrowing.expected_return_date),
        )
        self.assertEqual(
            data["actual_return_date"], self.borrowing.actual_return_date
        )
        self.assertEqual(data["book"], self.borrowing.book.title)

    def test_borrowing_detail_serializer(self) -> None:
        request = APIRequestFactory().get("/borrowing/")
        context = {"request": request}
        serializer = BorrowingDetailSerializer(self.borrowing, context=context)
        data = serializer.data
        self.assertEqual(data["id"], self.borrowing.id)
        self.assertEqual(data["borrow_date"], str(self.borrowing.borrow_date))
        self.assertEqual(
            data["expected_return_date"],
            str(self.borrowing.expected_return_date),
        )
        self.assertEqual(
            data["actual_return_date"], self.borrowing.actual_return_date
        )
        self.assertEqual(data["book"]["id"], self.borrowing.book.id)
