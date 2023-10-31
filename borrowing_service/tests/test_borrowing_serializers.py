from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory

from books_service.models import Book, Author
from borrowing_service.models import Borrowing
from borrowing_service.serializers.common import (
    BorrowingCreateSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
)
from borrowing_service.serializers.nested import BorrowingPaymentSerializer


class BorrowingSerializerTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@gmail.com", password="testpassword", is_staff=True
        )
        self.client.force_authenticate(self.user)
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
        self.assertIsInstance(data["payments"], list)
        self.assertEqual(
            len(data["payments"]), self.borrowing.payments.count()
        )

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
        self.assertIsInstance(data["payments"], list)
        self.assertEqual(
            len(data["payments"]), self.borrowing.payments.count()
        )

    def test_valid_borrowing_return(self) -> None:
        inventory = self.book.inventory
        self.assertIsNone(self.borrowing.actual_return_date)
        serializer = BorrowingReturnSerializer(
            instance=self.borrowing,
            data={"actual_return_date": timezone.now().date()},
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, inventory + 1)

    def test_already_returned_borrowing(self) -> None:
        self.borrowing.actual_return_date = timezone.now().date()
        self.borrowing.save()
        serializer = BorrowingReturnSerializer(
            instance=self.borrowing,
            data={"actual_return_date": timezone.now().date()},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "This borrowing has already been returned.",
            serializer.errors["non_field_errors"],
        )

    def test_borrowing_payment_serializer(self) -> None:
        serializer = BorrowingPaymentSerializer(self.borrowing)
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
        self.assertEqual(data["book"], self.borrowing.book.id)
