import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from tgbot.routers import (
    info_router,
    login_router,
    request_router,
    notify_router,
)

from tgbot.config import TOKEN


async def main() -> None:
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(info_router.router)
    login_router.initialize(bot)
    dp.include_router(login_router.router)
    dp.include_router(request_router.router)
    notify_router.initialize(bot)
    dp.include_router(notify_router.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
