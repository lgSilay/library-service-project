from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from borrowing_service.models import Borrowing
from tgbot.notificator import send_notification


@shared_task
def send_notification_task(message: str) -> None:
    send_notification(message)


@shared_task
def check_overdue_borrowings() -> None:
    overdue_borrowings = Borrowing.objects.filter(
        Q(expected_return_date__lt=timezone.now())
        & Q(actual_return_date__isnull=True)
    )
    message = "No borrowings overdue today!"
    if overdue_borrowings.exists():
        borrowings_str = "\n".join(
            str(borrowing) for borrowing in overdue_borrowings
        )
        message = f"Borrowings overdue:\n{borrowings_str}"
    send_notification(message)
