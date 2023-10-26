import asyncio
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest

from tgbot.bot_singleton import BotSingleton

router = Router()

bot = BotSingleton()


async def send_notification(receivers: list[int], notification: str):
    """Sends notification to all incoming users"""
    coroutines = [
        bot.send_message(receiver, notification) for receiver in receivers
    ]
    try:
        await asyncio.gather(*coroutines)
    except TelegramBadRequest:
        pass
