import stripe
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from django.contrib.auth import get_user_model

from books_service.models import Author, Book
from borrowing_service.models import Borrowing
from payments_service.models import Payment


class PaymentViewTests(TestCase):
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

    def test_renew_payment_session(self) -> None:
        payment = Payment.objects.create(
            status="expired",
            type="payment",
            borrowing=self.borrowing,
            session_url="http://example.com/payment",
            session_id="12345",
            expires_at=int(timezone.now().timestamp() + 3600),
            money_to_pay=50.00,
        )
        url = reverse("payments:renew_payment_session", args=[payment.pk])
        response = self.client.post(url)
        self.assertEqual(
            response.status_code, status.HTTP_307_TEMPORARY_REDIRECT
        )

    def test_renew_payment_session_non_expired_payment(self) -> None:
        payment = self.payment
        url = reverse("payments:renew_payment_session", args=[payment.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_success_paid_session(self) -> None:
        payment = self.payment
        stripe.checkout.Session.retrieve = lambda session_id: {
            "payment_status": "paid"
        }
        url = reverse("payments:payment-order-success")
        response = self.client.get(url, data={"session_id": "12345"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_success_not_paid_session(self) -> None:
        payment = self.payment
        stripe.checkout.Session.retrieve = lambda session_id: {
            "payment_status": "unpaid"
        }
        url = reverse("payments:payment-order-success")
        response = self.client.get(url, data={"session_id": "12345"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_success_no_session_id(self) -> None:
        url = reverse("payments:payment-order-success")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_cancel(self) -> None:
        url = reverse("payments:payment-order-cancel")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
