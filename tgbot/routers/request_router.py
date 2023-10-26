import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

# from tgbot.config import REQUEST_URL
router = Router()

REQUEST_URL = "http://127.0.0.1:8000/api/user/token/"


async def make_api_request():
    async with aiohttp.ClientSession() as session:
        data_to_post = {
            "email": "user2@email.com",
            "password": "GGduIU@"
        }
        async with session.post(REQUEST_URL, json=data_to_post) as response:
            print(response.status)
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
