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

    def test_borrowing_str(self) -> None:
        borrowing = self.create_borrowing(
            self.borrow_date, self.borrow_date + timezone.timedelta(days=1)
        )
        borrowing.save()
        self.assertEqual(
            str(borrowing), f"{self.book.title} borrowed by {self.user.email}"
        )

    def test_expected_return_date_is_later_than_borrow_date(self) -> None:
        borrowing = self.create_borrowing(
            self.borrow_date,
            self.borrow_date + timezone.timedelta(days=1),
            None,
        )
        borrowing.full_clean()

    def test_actual_return_date_is_later_than_borrow_date(self) -> None:
        borrowing = self.create_borrowing(
            self.borrow_date,
            self.borrow_date + timezone.timedelta(days=1),
            self.borrow_date + timezone.timedelta(days=1),
        )
        if borrowing.actual_return_date:
            borrowing.full_clean()
        else:
            with self.assertRaises(ValidationError):
                borrowing.full_clean()

    def test_borrowing_is_active(self) -> None:
        borrowing = self.create_borrowing(
            self.borrow_date, self.borrow_date + timezone.timedelta(days=1)
        )
        borrowing.save()
        self.assertEqual(
            borrowing.is_active, borrowing.actual_return_date is None
        )

    def test_borrowing_ordering(self) -> None:
        borrow_date = timezone.now().date()
        expected_return_dates = [
            borrow_date + timezone.timedelta(days=3),
            borrow_date + timezone.timedelta(days=1),
            borrow_date + timezone.timedelta(days=5),
        ]

        for expected_return_date in expected_return_dates:
            self.create_borrowing(borrow_date, expected_return_date).save()

        sorted_borrowings = Borrowing.objects.all()

        for i in range(1, len(sorted_borrowings)):
            self.assertTrue(
                sorted_borrowings[i - 1].expected_return_date
                <= sorted_borrowings[i].expected_return_date
            )
