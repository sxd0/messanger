from sqlalchemy import delete, insert, select, update
from app.database import async_session_maker
import logging



logger = logging.getLogger(__name__)

# Тут по сути контекстны менеджер с async_session_maker(который содержит в себе AsyncSession) заменяет сам AsyncSession и get_db

class BaseDAO:
    def __init__(self, model): # протестировать
        self.model = model

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            try:
                query = select(cls.model.__table__.columns).filter_by(**filter_by)
                result = await session.execute(query)
                return result.mappings().one_or_none()
            except Exception as e:
                logger.error(f"Error in find_one_or_none: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")
            
    @classmethod
    async def find_all(cls, offset: int = 0, limit: int = 100, **filter_by): # Добавлена пагинация ПРОВЕРИТЬ
        async with async_session_maker() as session:
            try:
                query = select(cls.model.__table__.columns).filter_by(**filter_by).offset(offset).limit(limit)
                result = await session.execute(query)
                return result.mappings().all()
            except Exception as e:
                logger.error(f"Error in find_all: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            try:
                query = insert(cls.model).values(**data)
                await session.execute(query)
                await session.commit()
            except Exception as e:
                logger.error(f"Error in add: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")

    @classmethod
    async def delete(cls, **filter_by):
        async with async_session_maker() as session:
            try:
                query = delete(cls.model).filter_by(**filter_by)
                await session.execute(query)
                await session.commit()
            except Exception as e:
                logger.error(f"Error in delete: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")

    @classmethod
    async def update(cls, filter_by, **data): # Добавлено возвращение изменяемых данных ПРОВЕРИТЬ
        async with async_session_maker() as session:
            try:
                query = update(cls.model).filter_by(**filter_by).values(**data).returning(cls.model)
                result = await session.execute(query)
                await session.commit()
                # await session.refresh(obj) # Протестировать
                return result.mappings().all()
            except Exception as e:
                logger.error(f"Error in update: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")

    @classmethod
    async def find_all_for_list(cls, field_name: str, values: list):
        if not hasattr(cls.model, field_name):
            raise ValueError(f"Field {field_name} does not exist in model {cls.model.__name__}")
        async with async_session_maker() as session:
            try:
                query = select(cls.model.__table__.columns).filter(getattr(cls.model, field_name).in_(values))
                result = await session.execute(query)
                return result.mappings().all()
            except Exception as e:
                logger.error(f"Error in find_all_for_list: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")