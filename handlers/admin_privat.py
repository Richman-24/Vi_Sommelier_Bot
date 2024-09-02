from aiogram import F, types, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from database.orm_query import orm_add_product
from keyboards.inline import get_callback_btns

admin_privat_router = Router()
# admin_privat_router.filter()  #### Добавить фильтр - только для only_family

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


######################### FSM для дабавления/изменения вина админом ###################
class AddDrink(StatesGroup):
    """Шаги состояний добавления напитка"""
    title=State()
    description=State()
    rating=State()
    category=State()
    image=State()

    # product_for_change = None
    
    texts = {
        "AddDrink:title": "Введите название заново:",
        "AddDrink:description": "Введите описание заново:",
        "AddDrink:category": "Выберите категорию  заново ⬆️",
        "AddDrink:rating": "Введите стоимость заново:",
        "AddDrink:image": "Этот стейт последний, поэтому...",
    }

# Отменяем FSM и сбрасываем состояния
@admin_privat_router.message(StateFilter("*"), Command("cancel"))
@admin_privat_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if not current_state:
        return
    
    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)

# Вернутся на шаг назад (на прошлое состояние)
@admin_privat_router.message(StateFilter("*"), Command("back"))
@admin_privat_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddDrink.title:
        await message.answer(
            'Предидущего шага нет, или введите название товара или напишите "отмена"'
        )
        return

    previous = None
    for step in AddDrink.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {AddDrink.texts[previous.state]}"
            )
            return
        previous = step

# Становимся в состояние ожидания ввода title
@admin_privat_router.callback_query(StateFilter(None), F.data=="add_wine")
async def add_drink(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название товара")
    await state.set_state(AddDrink.title)
    await callback.answer()

# Ловим данные для состояние title и потом меняем состояние на description
@admin_privat_router.message(AddDrink.title, F.text)
async def add_drink_name(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание товара")
    await state.set_state(AddDrink.description)

# Некорректные данные для состояние title
@admin_privat_router.message(AddDrink.title)
async def add_drink_name(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст названия товара")

# Ловим данные для состояние description и потом меняем состояние на rating
@admin_privat_router.message(AddDrink.description, F.text)
async def add_drink_name(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Поставьте оценку товара")
    await state.set_state(AddDrink.rating)

# Некорректные данные для состояние description
@admin_privat_router.message(AddDrink.description)
async def add_drink_name(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст описания товара")

# Ловим данные для состояние rating и потом меняем состояние на category
@admin_privat_router.message(AddDrink.rating, F.text)
async def add_drink_name(message: types.Message, state: FSMContext):
    await state.update_data(rating=message.text)
    await message.answer("(Временно - 1) Напишите категорию товара")
    await state.set_state(AddDrink.category)

# Некорректные данные для состояние rating
@admin_privat_router.message(AddDrink.rating)
async def add_drink_name(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите численную оценку товара")

# Ловим данные для состояние category и потом меняем состояние на image
@admin_privat_router.message(AddDrink.category, F.text)
async def add_drink_name(message: types.Message, state: FSMContext):
    await state.update_data(rating=message.text)
    await message.answer("Отправьте изображение товара!")
    await state.set_state(AddDrink.image)

# Ловим данные для состояние image и потом очищаем состояния
@admin_privat_router.message(AddDrink.image, F.photo)
async def add_drink_name(message: types.Message, state: FSMContext, session):
    data = await state.get_data()

    await state.update_data(image=message.photo[-1].file_id)
    await message.answer(f"Товар {data.get('title')} добавлен/изменен", reply_markup=ADMIN_KB)
    await orm_add_product(session, data)
    await state.clear()

# Ловим данные для состояние image и потом очищаем состояния
@admin_privat_router.message(AddDrink.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото товара")