from aiogram import Bot
from aiogram.enums import ParseMode

from tgbot.config import TOKEN


class BotSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
        return cls._instance.bot
