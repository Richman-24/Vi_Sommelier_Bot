from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import Bear, Wine, CategoryBear, CategoryWine

############ Админка: добавить/изменить/удалить вино\Пиво ########################
async def orm_add_product(session: AsyncSession, data: dict, table: str):

    base_obj_table = {
        'bear': Bear,
        'wine': Wine
    }

    obj = base_obj_table.get(table)(
        title=data["title"],
        description=data["description"],
        rating=int(data["rating"]),
        image=data["image"],
        category_id=int(data["category"]),
    )
    session.add(obj)
    await session.commit()

############################ Категории ######################################

category_obj_table = {
        'bear': CategoryBear,
        'wine': CategoryWine
    }

async def orm_get_categories(session: AsyncSession, table: str):
    query = select(category_obj_table.get(table))
    result = await session.execute(query)
    return result.scalars().all()

async def orm_create_categories(session: AsyncSession, categories: list, table: str):
    query = select(category_obj_table.get(table))
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([table(title=title) for title in categories]) 
    await session.commit()
