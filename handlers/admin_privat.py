from aiogram import F, types, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_product, orm_get_categories
from keyboards.inline import get_callback_btns

admin_privat_router = Router()
# admin_privat_router.filter()  #### Добавить фильтр - только для only_family

admin_choices={
        "Добавить вино":"add_wine", 
        "Добавить пиво":"add_bear", 
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
    category=State()
    description=State()
    rating=State()
    image=State()

    type_of_drink = None
    # product_for_change = None
    
    texts = {
        "AddDrink:title": "Введите название заново:",
        "AddDrink:category": "Выберите категорию  заново ⬆️",
        "AddDrink:description": "Введите описание заново:",
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
@admin_privat_router.callback_query(StateFilter(None), F.data=="add_bear")
async def add_drink(callback: types.CallbackQuery, state: FSMContext):
    AddDrink.type_of_drink = (
        'wine' if callback.data == "add_wine" else 'bear'
    )
    print(AddDrink.type_of_drink)
    await callback.message.answer("Введите название товара")
    await state.set_state(AddDrink.title)
    await callback.answer()

# Ловим данные для состояние title и потом меняем состояние на category
@admin_privat_router.message(AddDrink.title, F.text)
async def title(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(title=message.text)

    categories = await orm_get_categories(session, AddDrink.type_of_drink)
    btns = {category.title : str(category.id) for category in categories}
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddDrink.category)

# Некорректные данные для состояние title
@admin_privat_router.message(AddDrink.title)
async def title(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст названия товара")

######################### УЛАДИТЬ ВЫБОР КАТЕГОРИИ ВИНА и ПИВА ##################################
# Ловим данные для состояние category и потом меняем состояние на description
@admin_privat_router.callback_query(AddDrink.category)
async def add_drink_category(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_categories(session, AddDrink.type_of_drink)]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer("Введите описание товара")
        await state.set_state(AddDrink.description)
    else:
        await callback.message.answer('Выберите катеорию из кнопок.')
        await callback.answer()

# Ловим данные для состояние description и потом меняем состояние на rating
@admin_privat_router.message(AddDrink.description, F.text)
async def add_drink_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Поставьте оценку товара")
    await state.set_state(AddDrink.rating)

# Некорректные данные для состояние description
@admin_privat_router.message(AddDrink.description)
async def wrong_drink_description(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите текст описания товара")

# Ловим данные для состояние rating и потом меняем состояние на category
@admin_privat_router.message(AddDrink.rating, F.text)
async def add_drink_rating(message: types.Message, state: FSMContext):
    await state.update_data(rating=message.text)
    await message.answer("Отправьте изображение товара!")
    await state.set_state(AddDrink.image)

# Некорректные данные для состояние rating
@admin_privat_router.message(AddDrink.rating)
async def wrong_drink_rating(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите численную оценку товара")

# Ловим данные для состояние image и потом очищаем состояния
@admin_privat_router.message(AddDrink.image, F.photo)
async def add_drink_image(message: types.Message, state: FSMContext, session):
    await state.update_data(image=message.photo[-1].file_id)

    data = await state.get_data()
    await message.answer(f"Товар {data.get('title')} добавлен/изменен", reply_markup=ADMIN_KB)
    await orm_add_product(session, data, AddDrink.type_of_drink)
    await state.clear()

# Ловим данные для состояние image и потом очищаем состояния
@admin_privat_router.message(AddDrink.image)
async def wrong_drink_image(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото товара")