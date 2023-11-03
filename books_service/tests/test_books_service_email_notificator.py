import datetime

from unittest import mock
from django.conf import settings
from django.test import TestCase
from books_service.email_notice_package.email_notificator import (
    EmailNotificator,
)


class EmailNotificatorTest(TestCase):
    @mock.patch(
        "books_service.email_notice_package.email_notificator.send_templated_mail"
    )
    def test_send_sign_up_email(self, mock_send_mail) -> None:
        user_email = "user@example.com"
        settings.DEFAULT_FROM_EMAIL = "from@example.com"

        EmailNotificator.send_sing_up_email(user_email)

        mock_send_mail.assert_called_once_with(
            template_name="sign-up",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            context={
                "email": user_email,
                "date_joined": datetime.date.today(),
            },
        )

    @mock.patch(
        "books_service.email_notice_package.email_notificator.send_templated_mail"
    )
    def test_send_subscription_email(self, mock_send_mail) -> None:
        user_email = "user@example.com"
        author_full_name = "John Doe"
        settings.DEFAULT_FROM_EMAIL = "from@example.com"

        EmailNotificator.send_subscription_email(user_email, author_full_name)

        mock_send_mail.assert_called_once_with(
            template_name="subscribe-manage",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            context={
                "email": user_email,
                "date_subscription": datetime.date.today(),
                "author_full_name": author_full_name,
                "status": True,
            },
        )
