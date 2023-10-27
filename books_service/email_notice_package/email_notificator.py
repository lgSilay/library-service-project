from datetime import datetime

from templated_email import send_templated_mail
from django.conf import settings


class EmailNotificator:
    @staticmethod
    def send_sing_up_email(user_email: str) -> None:
        send_templated_mail(
            template_name="sign-up",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            context={
                "email": user_email,
                "date_joined": datetime.now().date()
            }
        )

    @staticmethod
    def send_subscription_email(
            user_email: str,
            author_full_name: str,
            date_subscription: datetime = datetime.now().date(),
            status: bool = True
    ) -> None:
        send_templated_mail(
            template_name="subscribe-manage",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            context={
                "email": user_email,
                "date_subscription": date_subscription,
                "author_full_name": author_full_name,
                "status": status,
            }
        )
