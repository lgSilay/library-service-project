import os

import requests
from dotenv import load_dotenv
from requests import HTTPError


def send_notification(receivers: list[int], notification: str):
    """Send message to admins in private telegram chat"""
    load_dotenv()
    token = os.environ.get("TOKEN")
    for chat_id in receivers:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": notification,
        }
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
        except HTTPError:
            return receivers
