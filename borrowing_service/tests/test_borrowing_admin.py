from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite

from borrowing_service.models import Borrowing
from borrowing_service.admin import BorrowingAdmin


class BorrowingAdminTest(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="admin@admin.com", password="admin_password"
        )
        self.factory = RequestFactory()
        self.client = Client()
        self.client.login(username="admin", password="admin_password")

    def test_borrowing_admin_list_display(self) -> None:
        site = AdminSite()
        borrowing_admin = BorrowingAdmin(Borrowing, site)
        request = self.factory.get("/admin/borrowing_service/borrowing/")
        request.user = self.user

        list_display = borrowing_admin.get_list_display(request)
        self.assertIn("id", list_display)
        self.assertIn("borrow_date", list_display)
        self.assertIn("expected_return_date", list_display)
        self.assertIn("actual_return_date", list_display)
        self.assertIn("book", list_display)

    def test_borrowing_admin_search_fields(self) -> None:
        site = AdminSite()
        borrowing_admin = BorrowingAdmin(Borrowing, site)

        search_fields = borrowing_admin.search_fields
        self.assertEqual(search_fields, ("book__title",))

    def test_borrowing_admin_sortable_by(self) -> None:
        site = AdminSite()
        borrowing_admin = BorrowingAdmin(Borrowing, site)
        request = self.factory.get("/admin/borrowing_service/borrowing/")
        request.user = self.user

        sortable_by = borrowing_admin.get_sortable_by(request)
        self.assertEqual(sortable_by, ("id",))
