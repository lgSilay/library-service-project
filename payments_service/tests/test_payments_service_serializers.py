from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from books_service.models import Author, Book
from borrowing_service.models import Borrowing
from payments_service.models import Payment
from payments_service.serializers.common import (
    PaymentDetailSerializer,
    PaymentListSerializer,
)
from payments_service.serializers.nested import PaymentBorrowingSerializer


class PaymentSerializerTest(TestCase):
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
            expires_at=int(timezone.now().timestamp() + 3600),
            money_to_pay=50.00,
        )

    def test_payment_detail_serializer(self) -> None:
        serializer = PaymentDetailSerializer(instance=self.payment)
        data = serializer.data
        self.assertEqual(data["id"], self.payment.id)
        self.assertEqual(data["type"], self.payment.type)
        self.assertEqual(data["status"], self.payment.status)
        self.assertEqual(data["session_url"], self.payment.session_url)
        self.assertEqual(data["expires_at"], self.payment.expires_at)
        self.assertEqual(
            data["money_to_pay"],
            str("{:.2f}".format(self.payment.money_to_pay)),
        )

    def test_payment_list_serializer(self) -> None:
        serializer = PaymentListSerializer(instance=self.payment)
        data = serializer.data
        self.assertEqual(data["id"], self.payment.id)
        self.assertEqual(data["type"], self.payment.type)
        self.assertEqual(data["status"], self.payment.status)
        self.assertEqual(data["borrowing"], self.book.title)
        self.assertEqual(data["session_url"], self.payment.session_url)
        self.assertEqual(data["expires_at"], self.payment.expires_at)
        self.assertEqual(
            data["money_to_pay"],
            str("{:.2f}".format(self.payment.money_to_pay)),
        )

    def test_payment_borrowing_serializer(self) -> None:
        serializer = PaymentBorrowingSerializer(instance=self.payment)
        data = serializer.data
        self.assertEqual(data["id"], self.payment.id)
        self.assertEqual(data["type"], self.payment.type)
        self.assertEqual(data["status"], self.payment.status)
        self.assertEqual(data["session_url"], self.payment.session_url)
        self.assertEqual(
            data["money_to_pay"],
            str("{:.2f}".format(self.payment.money_to_pay)),
        )
