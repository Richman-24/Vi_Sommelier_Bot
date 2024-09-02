from aiogram import F, types, Router
from aiogram.filters import Command

from keyboards.inline import get_callback_btns

admin_privat_router = Router()

admin_choices={
        "Добавить":"add_wine", 
        "Изменить":"edit_wine", 
    }

ADMIN_KB = get_callback_btns(
    btns=admin_choices
)

@admin_privat_router.message(Command('admin'))
async def command_admin_handler(message: types.Message) -> None:
    await message.answer(
        " ----- \n Adminskaya panel \n -----",
        reply_markup=ADMIN_KB
        )
    
@admin_privat_router.callback_query(F.data.in_(admin_choices.values()))
async def admin_wine_activity(callback: types.CallbackQuery):
    await callback.message.answer("[Добавить]\n[Редактировать]\n[Удалить]")
    await callback.answer()