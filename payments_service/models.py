from django.conf import settings
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
    money_to_pay = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ("status",)

    def __str__(self) -> str:
        return f"{self.type} ({self.status})"
