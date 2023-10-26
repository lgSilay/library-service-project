from typing import Any, Dict

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram.fsm.state import State, StatesGroup

router = Router()


class Form(StatesGroup):
    username = State()
    password = State()


@router.message(Command("login"))
async def command_login(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.username)
    await message.answer(
        "Enter your username:",
    )


@router.message(Form.username)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(username=message.text)
    await state.set_state(Form.password)
    await message.answer(
        f"Enter your password:"
    )


@router.message(Form.password)
async def process_password(message: Message, state: FSMContext) -> None:
    data = await state.update_data(password=message.text)
    await state.clear()
    await perform_login(message=message, data=data)


async def perform_login(message: Message, data: Dict[str, Any]) -> None:
    username = data["username"]
    password = data["password"]
    await message.answer(f"{username}, {password}")
