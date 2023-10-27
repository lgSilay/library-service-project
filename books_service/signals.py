from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from user.models import User
from .models import Author, Subscription
from books_service.email_notice_package.email_notificator import EmailNotificator


@receiver(post_save, sender=User)
def user_profile_created(sender, instance, created, **kwargs):
    if created:
        EmailNotificator.send_sing_up_email(instance.email)


@receiver(m2m_changed, sender=Author.subscribers.through)
def send_subscription_notification(sender, instance, **kwargs):
    author = Author.objects.get(
        pk=tuple(
            kwargs.get("pk_set"))[0]
    )

    if kwargs.get("action") == "post_add":
        EmailNotificator.send_subscription_email(
            user_email=instance.email,
            author_full_name=author.full_name
        )
    elif kwargs.get("action") == "pre_remove":
        subscription_instance = Subscription.objects.get(
            user=instance, author=author
        )
        EmailNotificator.send_subscription_email(
            user_email=instance.email,
            author_full_name=author.full_name,
            status=False,
            date_subscription=subscription_instance.subscription_started
        )
