from django.db.models.signals import post_save, m2m_changed
from books_service.models import Author

from books_service.signals import (
    user_profile_created,
    send_subscription_notification,
)
from user.models import User

post_save.connect(user_profile_created, sender=User)
m2m_changed.connect(
    send_subscription_notification, sender=Author.subscribers.through
)
