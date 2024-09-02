from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Wine


############ Админка: добавить/изменить/удалить вино ########################
async def orm_add_product(session: AsyncSession, data: dict):
    obj = Wine(
        title=data["title"],
        description=data["description"],
        rating=float(data["rating"]),
        image=data["image"],
        category=int(data["category"]),
    )
    session.add(obj)
    await session.commit()