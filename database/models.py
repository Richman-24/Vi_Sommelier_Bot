from typing import Annotated

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, SmallInteger, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

str_150 = Annotated[str, 150]

class BaseModel(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class CategoryWine(BaseModel):
    __tablename__ = 'category_wine'

    title: Mapped[str_150]


class Wine(BaseModel):
    __tablename__ = 'wine'

    title: Mapped[str_150]
    description: Mapped[str] = mapped_column(Text)
    image: Mapped[str_150] #пока что будем хранить ссылку на изображение в базе ТГ, а там придумаем. 
    rating: Mapped[int] = mapped_column(SmallInteger)
    category: Mapped['CategoryWine'] = relationship(backref='wine')

# class Bear(BaseModel):
#     __tablename__ = 'bear'

#     title: Mapped[str_150]
#     description: Mapped[str] = mapped_column(Text)
#     image: Mapped[str_150] #пока что будем хранить ссылку на изображение в базе ТГ, а там придумаем. 
#     rating: Mapped[int] = mapped_column(SmallInteger)
#     category: Mapped['CategoryWine'] = relationship(backref='wine')
