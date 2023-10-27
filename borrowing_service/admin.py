from django.contrib import admin

from .models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
        "book",
    )
    search_fields = ("book__title",)
    sortable_by = ("id",)
