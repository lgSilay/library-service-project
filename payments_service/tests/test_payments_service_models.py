from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from books_service.models import Author, Book
from borrowing_service.models import Borrowing
from payments_service.models import Payment


class PaymentModelTest(TestCase):
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
        self.payment = Payment.objects.create(
            status="pending",
            type="payment",
            borrowing=self.borrowing,
            session_url="http://example.com/payment",
            session_id="12345",
            expires_at=timezone.now().timestamp() + 3600,
            money_to_pay=50.00,
        )

    def test_payment_creation(self) -> None:
        self.assertEqual(self.payment.status, "pending")
        self.assertEqual(self.payment.type, "payment")
        self.assertEqual(self.payment.borrowing, self.borrowing)
        self.assertEqual(
            self.payment.session_url, "http://example.com/payment"
        )
        self.assertEqual(self.payment.session_id, "12345")
        self.assertAlmostEqual(self.payment.money_to_pay, 50.00, places=2)

    def test_payment_str_method(self) -> None:
        expected_str = f"{self.borrowing} 50.0$ payment (pending)"
        self.assertEqual(str(self.payment), expected_str)

    def test_payment_ordering(self) -> None:
        payment1 = Payment.objects.create(
            status="paid",
            type="fee",
            borrowing=self.borrowing,
            session_url="http://example.com/payment",
            session_id="12345",
            expires_at=timezone.now().timestamp() + 3600,
            money_to_pay=30.00,
        )
        payment2 = self.payment
        payments = Payment.objects.all()
        self.assertEqual(payments[0], payment1)
        self.assertEqual(payments[1], payment2)
