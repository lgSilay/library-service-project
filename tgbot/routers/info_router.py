from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help", "start"))
async def command_help_handler(message: Message) -> None:
    await message.answer(
        "It is a bot where you can receive notifications.\n"
        "Please, use /login to attach your website profile."
    )
