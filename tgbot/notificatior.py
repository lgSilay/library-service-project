import requests
from django.contrib.auth import get_user_model

import tgbot.config


def send_notification(notification: str):
    """Send message to admins in private telegram chat"""
    receivers = (
        get_user_model()
        .objects.filter(is_staff=1, telegram_id__isnull=False)
        .distinct()
        .values_list("telegram_id", flat=True)
    )
    receivers = list(receivers)
    token = tgbot.config.TOKEN
    for chat_id in receivers:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": notification,
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
