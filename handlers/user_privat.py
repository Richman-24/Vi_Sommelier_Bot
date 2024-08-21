from aiogram import types, Router,  html
from aiogram.filters import CommandStart, Command

user_privat_router = Router()


@user_privat_router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

@user_privat_router.message(Command('menu'))
async def command_start_handler(message: types.Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@user_privat_router.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender
    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")