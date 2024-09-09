import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from common.texts_for_database import WINE_CATEGORIES, BEAR_CATEGORIES
from database.models import BaseModel, CategoryWine, CategoryBear
from database.orm_query import orm_create_categories

engine = create_async_engine(
    url=os.getenv('DB_LITE'),
    echo=False,
    # pool_size=5,
    # max_overflow=10
)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    
    async with session_maker() as session:
        await orm_create_categories(session, WINE_CATEGORIES, 'wine')
        await orm_create_categories(session, BEAR_CATEGORIES, 'bear')


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)  