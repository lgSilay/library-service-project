from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from django.utils import timezone


from books_service.models import Book, Author
from borrowing_service.models import Borrowing
from borrowing_service.serializers.common import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)

BORROWING_URL = reverse("borrowing_service:borrowing-list")


def sample_borrowing(
    user, book, expected_return_date, actual_return_date=None
) -> Borrowing:
    return Borrowing.objects.create(
        user=user,
        book=book,
        expected_return_date=expected_return_date,
        actual_return_date=actual_return_date,
    )


class UnauthenticatedBorrowingViewSetTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingViewSetTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)

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

    def test_list_borrowings(self) -> None:
        borrowing1 = sample_borrowing(
            self.user,
            self.book,
            timezone.now().date() + timezone.timedelta(days=7),
        )
        borrowing2 = sample_borrowing(
            self.user,
            self.book,
            timezone.now().date() + timezone.timedelta(days=7),
        )
        res = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_borrowings_by_user_id(self) -> None:
        borrowing1 = sample_borrowing(
            self.user,
            self.book,
            timezone.now().date() + timezone.timedelta(days=7),
        )
        borrowing2 = sample_borrowing(
            self.user,
            self.book,
            timezone.now().date() + timezone.timedelta(days=7),
        )

        other_user = get_user_model().objects.create_user(
            email="otheruser@example.com", password="otherpassword"
        )
        borrowing3 = sample_borrowing(
            other_user,
            self.book,
            timezone.now().date() + timezone.timedelta(days=7),
        )

        res = self.client.get(BORROWING_URL, {"user_id": f"{self.user.id}"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_filter_borrowings_by_is_active(self) -> None:
        borrowing1 = sample_borrowing(
            self.user,
            self.book,
            timezone.now().date() + timezone.timedelta(days=7),
        )
        borrowing2 = sample_borrowing(
            self.user,
            self.book,
            timezone.now().date() + timezone.timedelta(days=7),
        )
        borrowing3 = sample_borrowing(
            self.user,
            self.book,
            timezone.now().date() + timezone.timedelta(days=7),
            timezone.now().date() + timezone.timedelta(days=7),
        )

        res = self.client.get(BORROWING_URL, {"is_active": "true"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_retrieve_borrowing_detail(self) -> None:
        borrowing = sample_borrowing(
            self.user,
            self.book,
            timezone.now().date() + timezone.timedelta(days=7),
        )

        url = reverse(
            "borrowing_service:borrowing-detail", args=[borrowing.id]
        )
        request = APIRequestFactory().get("/borrowing/")
        context = {"request": request}

        serializer = BorrowingDetailSerializer(borrowing, context=context)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing_out_of_stock(self) -> None:
        self.book.inventory = 0
        self.book.save()
        payload = {
            "book": self.book.id,
            "expected_return_date": "2023-11-01",
        }
        res = self.client.post(BORROWING_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing(self) -> None:
        borrowing = sample_borrowing(
            self.user,
            self.book,
            timezone.now().date() + timezone.timedelta(days=7),
        )
        url = reverse("borrowing_service:order_return", args=[borrowing.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)

    def test_return_borrowing_already_returned(self) -> None:
        borrowing = sample_borrowing(
            self.user,
            self.book,
            timezone.now().date() + timezone.timedelta(days=7),
            timezone.now().date() + timezone.timedelta(days=7),
        )
        url = reverse(
            "borrowing_service:order_return", args=[borrowing.id]
        )
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
