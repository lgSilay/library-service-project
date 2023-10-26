import asyncio

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from tgbot.routers.notify_router import send_notification

from books_service.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    @property
    def is_active(self) -> bool:
        return self.actual_return_date is None

    @staticmethod
    def validate_date(
        expected_return_date,
        actual_return_date,
        error_to_raise,
        borrow_date=None
    ) -> None:
        if not borrow_date:
            borrow_date = timezone.now().date()
        if expected_return_date < borrow_date:
            raise error_to_raise(
                {
                    "expected_return_date": (
                        "Expected return date "
                        "must be later than Borrow date"
                    )
                }
            )
        if actual_return_date and actual_return_date < borrow_date:
            raise error_to_raise(
                {
                    "actual_return_date": (
                        "Actual return date must be later than Borrow date"
                    )
                }
            )

    def clean(self) -> None:
        Borrowing.validate_date(
            self.expected_return_date,
            self.actual_return_date,
            ValidationError,
            self.borrow_date
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        ordering = ["expected_return_date"]

    def __str__(self) -> str:
        return f"{self.book.title} borrowed by {self.user.email}"


@receiver(post_save, sender=Borrowing)
def notify_telegram(sender, instance, created, **kwargs):
    if created:
        stuff = (
            get_user_model()
            .objects.filter(is_staff=1, telegram_id__isnull=False)
            .distinct()
            .values_list("telegram_id", flat=True)
        )
        stuff = list(stuff)
        info = str(instance)
        asyncio.run(send_notification(stuff, info))
        # TODO Celery task instead of asyncio
