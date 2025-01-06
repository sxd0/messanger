from typing import List

from sqlalchemy import select
from app.dao.base import BaseDAO
from app.users.models import Users
from app.database import async_session_maker


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def search_by_nickname(cls, query: str) -> List[Users]:
        async with async_session_maker() as session:
            query = select(cls.model).filter(cls.model.nickname.ilike(f"%{query}%"))
            result = await session.execute(query)
            return result.scalars().all()