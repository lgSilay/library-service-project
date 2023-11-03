from django.test import TestCase
from django.contrib.auth import get_user_model

from user.models import User


class UserManagerTests(TestCase):
    def test_create_user(self):
        User = get_user_model()

        email = "testuser@example.com"
        password = "testpassword"
        user = User.objects.create_user(email, password)

        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.email, email)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(password))

    def test_create_superuser(self):
        User = get_user_model()

        email = "superuser@example.com"
        password = "superpassword"
        superuser = User.objects.create_superuser(email, password)

        self.assertEqual(superuser.email, email)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.check_password(password))


class UserModelTests(TestCase):
    def test_fields(self):
        user = User(email="test@example.com", telegram_id=12345)
        user.save()
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.telegram_id, 12345)

    def test_unique_email(self):
        user1 = User(email="test@example.com", telegram_id=12345)
        user1.save()
        user2 = User(email="test@example.com", telegram_id=67890)
        with self.assertRaises(Exception):
            user2.save()

    def test_null_fields(self):
        user = User(email="test@example.com")
        user.save()
        self.assertEqual(user.email, "test@example.com")
        self.assertIsNone(user.telegram_id)

    def test_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_required_fields(self):
        self.assertEqual(User.REQUIRED_FIELDS, [])

    def test_set_password(self):
        email = "testuser@example.com"
        password = "testpassword"
        user = User(email=email)
        user.set_password(password)
        self.assertTrue(user.check_password(password))


class GeneralUserTests(TestCase):
    def test_create_and_retrieve_user(self):
        User = get_user_model()
        email = "testuser@example.com"
        password = "testpassword"
        user = User.objects.create_user(email, password)

        retrieved_user = User.objects.get(email=email)
        self.assertEqual(retrieved_user.email, email)

    def test_authenticate_user(self):
        User = get_user_model()
        email = "testuser@example.com"
        password = "testpassword"
        user = User.objects.create_user(email, password)

        authenticated_user = User.objects.get(email=email)
        self.assertTrue(authenticated_user.check_password(password))

    def test_create_superuser_error(self):
        User = get_user_model()
        email = "superuser@example.com"
        password = "superpassword"
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email, password, is_staff=False, is_superuser=False
            )
