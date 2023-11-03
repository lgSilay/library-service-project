import logging
import os
from django.contrib.auth import get_user_model

import requests
from dotenv import load_dotenv
from requests import HTTPError


logger = logging.getLogger("tg_bot")


def send_notification(notification: str):
    """Send message to admins in private telegram chat"""
    load_dotenv()
    token = os.environ.get("TOKEN")
    recievers = (
        get_user_model()
        .objects.filter(is_staff=True, telegram_id__isnull=False)
        .distinct()
        .values_list("telegram_id", flat=True)
    )
    recievers = list(recievers)
    for chat_id in recievers:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": notification,
        }
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
        except HTTPError:
            logger.error(f"Wrong telegram id {chat_id}")
            return recievers
