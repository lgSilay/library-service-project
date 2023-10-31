from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

from books_service.models import Book, Author
from borrowing_service.models import Borrowing


class BorrowingModelTest(TestCase):
    def setUp(self) -> None:
        self.borrow_date = timezone.now().date()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test123",
            first_name="test_first",
            last_name="test_last",
        )
        self.book = Book.objects.create(
            title="Test_Book",
            author=Author.objects.create(
                first_name="Test",
                last_name="Test",
            ),
            cover="hard",
            inventory=4,
            daily_fee=150.00,
        )

    def create_borrowing(
        self, borrow_date, expected_return_date, actual_return_date=None
    ) -> Borrowing:
        return Borrowing(
            borrow_date=borrow_date,
            expected_return_date=expected_return_date,
            actual_return_date=actual_return_date,
            book=self.book,
            user=self.user,
        )

    def test_expected_return_date_is_later_than_borrow_date(self) -> None:
        borrowing = self.create_borrowing(
            self.borrow_date,
            self.borrow_date + timezone.timedelta(days=1),
            None,
        )
        borrowing.clean()

    def test_actual_return_date_is_later_than_borrow_date(self) -> None:
        borrowing = self.create_borrowing(
            self.borrow_date,
            self.borrow_date + timezone.timedelta(days=1),
            self.borrow_date + timezone.timedelta(days=1),
        )
        if borrowing.actual_return_date:
            borrowing.clean()
        else:
            with self.assertRaises(ValidationError):
                borrowing.clean()

    def test_is_active_property(self) -> None:
        borrowing = self.create_borrowing(
            self.borrow_date,
            self.borrow_date + timezone.timedelta(days=1),
            None,
        )
        self.assertTrue(borrowing.is_active)

        borrowing.actual_return_date = self.borrow_date + timezone.timedelta(
            days=2
        )
        borrowing.clean()
        self.assertFalse(borrowing.is_active)

    def test_borrowing_string_representation(self) -> None:
        borrowing = self.create_borrowing(
            self.borrow_date,
            self.borrow_date + timezone.timedelta(days=1),
            None,
        )
        expected_string = (
            f"'{borrowing.book.title}' borrowed by {borrowing.user.email}"
        )
        self.assertEqual(str(borrowing), expected_string)
