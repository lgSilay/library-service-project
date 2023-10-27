from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowing_service.models import Borrowing
from borrowing_service.tasks import send_notification_task


@receiver(post_save, sender=Borrowing)
def notify_telegram(sender, instance, created, **kwargs):
    if created:
        send_notification_task.delay(str(instance))
