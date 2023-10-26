from typing import Any, Dict
import aiohttp
from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram.fsm.state import State, StatesGroup

from tgbot.config import LOGIN_URL, REQUEST_URL
from tgbot.bot_singleton import BotSingleton

router = Router()
bot = BotSingleton()


class Form(StatesGroup):
    email = State()
    password = State()


@router.message(Command("login"))
async def command_login(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.email)
    await message.answer(
        "Enter your email:",
    )


@router.message(Form.email)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(email=message.text)
    await state.set_state(Form.password)
    await message.answer(
        f"Enter your password:"
    )


# noinspection PyUnresolvedReferences
@router.message(Form.password)
async def process_password(message: Message, state: FSMContext) -> None:
    data = await state.update_data(password=message.text)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await state.clear()
    await perform_login(message=message, data=data)


async def perform_login(message: Message, data: Dict[str, Any]) -> None:
    if message.chat.type != ChatType.PRIVATE:
        await message.answer(
            f"Login is available only in private conversion with bot."
        )
        return
    email = data["email"]
    password = data["password"]
    async with aiohttp.ClientSession() as session:
        login_data = {
            "email": email,
            "password": password,
        }
        async with session.post(LOGIN_URL, json=login_data) as response:
            print(response.status)
            if response.status == 200:
                data = await response.json()
                token = data["access"]
                await connect_to_user(message, token)
            else:
                await message.answer(
                    f"Error occurred. {response.status}. Please, check your"
                    "credentials. "
                )


async def connect_to_user(message: Message, token: str):
    telegram_id = message.from_user.id
    headers = {
        "Authorization": f"Bearer {token}",
    }
    data_to_patch = {
        "telegram_id": telegram_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.patch(REQUEST_URL, json=data_to_patch,
                                 headers=headers) as response:
            if response.status == 200:
                await message.answer(
                    f"Success! Now your account attached to this profile."
                )
            else:
                await message.answer(
                    f"Error occurred. {response.status}"
                )


def initialize(bot_instance):
    global bot
    bot = bot_instance
