import asyncio
import logging
import sys

from aiogram import Dispatcher
from tgbot.routers import (
    info_router,
    login_router,
)

from tgbot.bot_singleton import BotSingleton


async def main() -> None:
    bot = BotSingleton()
    dp = Dispatcher()
    dp.include_router(info_router.router)
    dp.include_router(login_router.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
