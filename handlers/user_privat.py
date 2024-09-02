from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command

from keyboards.inline import get_callback_btns

user_privat_router = Router()

_choices = {
            "Красное":"red",
            "Белое":"white",
            "Игристое":"champaign",
            "Фруктовое":"fruit"
    }

TYPES_OF_WINE_KB = get_callback_btns(
    btns=_choices,
    sizes=(2,2)
)

# Обрабаывает команду /start
@user_privat_router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(f"Бот запущен и работает!")

# Обрабаывает команду /wine
@user_privat_router.message(Command('wine'))
async def command_wine_handler(message: types.Message) -> None:
    
    await message.answer(
        f"Итак, что будем пить сегодня?",
        reply_markup=TYPES_OF_WINE_KB
    )

# Обрабаывает нажатие на кнопку type_of_wine
@user_privat_router.callback_query(F.data.in_(_choices.values()))
async def type_of_wine_handler(callback: types.CallbackQuery):
    # Тут идёт запрос к БД по типам вина. 
    await callback.message.answer(f"Вот тебе результат по запросу {callback.data}")
    await callback.answer()



# @user_privat_router.message()
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