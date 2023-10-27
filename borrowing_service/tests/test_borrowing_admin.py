from django.contrib import admin
from django.test import TestCase

from borrowing_service.models import Borrowing


class BorrowingAdminTest(TestCase):
    def test_borrowing_admin_should_be_registered(self) -> None:
        self.assertIn(Borrowing, admin.site._registry)
