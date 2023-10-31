from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.utils import timezone

from books_service.models import Author, Book, Subscription
from user.models import User


class AuthorModelTest(TestCase):
    def setUp(self) -> None:
        self.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
        )

    def test_create_author(self) -> None:
        self.assertEqual(self.author.full_name, "John Doe")
        self.assertEqual(str(self.author), "John Doe")

    def test_create_author_with_profile_image(self) -> None:
        image = SimpleUploadedFile(
            "test_image.jpg", b"image_content", content_type="image/jpeg"
        )
        self.author.author_profile_image = image
        self.author.save()
        self.assertIsNotNone(self.author.author_profile_image)

    def test_create_subscription(self) -> None:
        user = User.objects.create_user(
            email="testuser@gmail.com", password="testpassword"
        )
        subscription = Subscription.objects.create(
            author=self.author, user=user, subscription_started=timezone.now()
        )
        expected_str = f"{user} subscribed to {self.author.full_name} since {timezone.now().date()}"
        self.assertEqual(str(subscription), expected_str)


class BookModelTest(TestCase):
    def setUp(self) -> None:
        self.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
        )

    def test_create_book(self) -> None:
        book = Book.objects.create(
            title="Test Book",
            author=self.author,
            cover="hard",
            inventory=5,
            daily_fee=10.00,
        )
        self.assertEqual(
            str(book),
            "'Test Book' written by John Doe",
        )

    def test_negative_inventory_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            Book.objects.create(
                title="Test Book",
                author=self.author,
                cover="hard",
                inventory=-5,
                daily_fee=10.00,
            )
