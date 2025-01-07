from typing import List

from sqlalchemy import select
from app.dao.base import BaseDAO
from app.users.models import Users
from app.database import async_session_maker


class UsersDAO(BaseDAO): # Изучить
    model = Users

    @classmethod
    async def search_by_nickname(cls, query: str) -> List[Users]:
        async with async_session_maker() as session:
            query = select(cls.model).filter(cls.model.name.ilike(f"%{query}%"))
            result = await session.execute(query)
            return result.scalars().all()
        
    @classmethod
    async def find_names_by_ids(cls, user_ids: List[int]) -> List[str]:
        async with async_session_maker() as session:
            query = select(cls.model.name).filter(cls.model.id.in_(user_ids))
            result = await session.execute(query)
            return result.scalars().all()