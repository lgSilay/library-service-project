import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from tgbot.config import REQUEST_URL
router = Router()


async def make_api_request():
    async with aiohttp.ClientSession() as session:
        async with session.get(REQUEST_URL) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None


@router.message(Command("request"))
async def api_request_handler(message: Message):
    data = await make_api_request()
    if data:
        await message.answer(f"Response: {data}")
    else:
        await message.answer(
            "Unexpected error occurred during the connection to API."
        )
