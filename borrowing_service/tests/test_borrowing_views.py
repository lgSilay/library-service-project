from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status

from books_service.models import Book, Author
from borrowing_service.models import Borrowing
from borrowing_service.serializers import (
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
        borrowing1 = sample_borrowing(self.user, self.book, "2023-10-30")
        borrowing2 = sample_borrowing(self.user, self.book, "2023-11-15")

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_borrowings_by_user_id(self) -> None:
        borrowing1 = sample_borrowing(self.user, self.book, "2023-10-30")
        borrowing2 = sample_borrowing(self.user, self.book, "2023-11-15")

        other_user = get_user_model().objects.create_user(
            email="otheruser@example.com", password="otherpassword"
        )
        borrowing3 = sample_borrowing(other_user, self.book, "2023-11-05")

        res = self.client.get(BORROWING_URL, {"user_id": f"{self.user.id}"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_filter_borrowings_by_is_active(self) -> None:
        borrowing1 = sample_borrowing(self.user, self.book, "2023-10-30")
        borrowing2 = sample_borrowing(self.user, self.book, "2023-11-15")
        borrowing3 = sample_borrowing(
            self.user, self.book, "2023-11-20", "2023-11-22"
        )

        res = self.client.get(BORROWING_URL, {"is_active": "true"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_borrowing_detail(self) -> None:
        borrowing = sample_borrowing(self.user, self.book, "2023-10-30")

        url = reverse(
            "borrowing_service:borrowing-detail", args=[borrowing.id]
        )
        request = APIRequestFactory().get("/borrowing/")
        context = {"request": request}

        serializer = BorrowingDetailSerializer(borrowing, context=context)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self) -> None:
        payload = {
            "book": self.book.id,
            "expected_return_date": "2023-11-01",
        }
        res = self.client.post(BORROWING_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
