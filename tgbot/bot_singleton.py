import os

from aiogram import Bot
from aiogram.enums import ParseMode
from dotenv import load_dotenv


class BotSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            load_dotenv()
            token = os.environ.get("TOKEN")
            cls._instance.bot = Bot(token=token, parse_mode=ParseMode.HTML)
        return cls._instance.bot
