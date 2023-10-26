import asyncio
from aiogram import Router

router = Router()
Bot = None


async def send_notification(receivers: list[int], notification: str):
    """Sends notification to all incoming users"""
    coroutines = [
        bot.send_message(receiver, notification) for receiver in receivers
    ]
    await asyncio.gather(*coroutines)


def initialize(bot_instance):
    global bot
    bot = bot_instance
