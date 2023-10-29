from django.utils import timezone
from celery import shared_task

from payments_service.models import Payment


@shared_task
def check_expired_payments() -> None:
    current_timestamp = timezone.now().timestamp()
    expired_payments = Payment.objects.filter(
        status="pending", expires_at__lt=current_timestamp
    )
    for payment in expired_payments:
        payment.status = "expired"
    Payment.objects.bulk_update(expired_payments, ["status"])
