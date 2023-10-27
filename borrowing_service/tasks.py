from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from borrowing_service.models import Borrowing
from tgbot.notificatior import send_notification


@shared_task
def send_notification_task(message: str) -> None:
    send_notification(message)


@shared_task
def check_overdue_borrowings() -> None:
    overdue_borrowings = Borrowing.objects.filter(
        Q(expected_return_date__lt=timezone.now())
        & Q(actual_return_date__isnull=True)
    )
    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            chat_id = borrowing.user.telegram_id
            ...
    else:
        ...
        print("No borrowings overdue today!")
