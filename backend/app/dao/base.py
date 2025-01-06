from sqlalchemy import delete, insert, select, update
from app.database import async_session_maker



class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().one_or_none()
        
    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete(cls, **filter_by):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(**filter_by)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def update(cls, filter_by, **data):
        async with async_session_maker() as session:
            query = update(cls.model).filter_by(**filter_by).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def find_all_for_list(cls, field_name: str, values: list):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter(getattr(cls.model, field_name).in_(values))
            result = await session.execute(query)
            return result.mappings().all()