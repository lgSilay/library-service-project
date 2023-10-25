from django.db import models

from borrowing_service.models import Borrowing


class Payment(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
    )
    TYPE_CHOICES = (
        ("payment", "Payment"),
        ("fee", "Fee"),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    borrowing = models.ForeignKey(
        Borrowing, related_name="payments", on_delete=models.CASCADE
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)

    @property
    def money_to_pay(self) -> float:
        return (
            self.borrowing.book.daily_fee
            * (
                self.borrowing.expected_return_date
                - self.borrowing.borrow_date
            ).days
        )

    class Meta:
        ordering = ("status",)

    def __str__(self) -> str:
        return f"{self.type} ({self.status})" 
