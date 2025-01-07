from sqlalchemy import select
from app.chats.models import Chats, Participants
from app.dao.base import BaseDAO
from app.database import async_session_maker


class ChatsDAO(BaseDAO):
    model = Chats

    @classmethod
    async def find_last_created_chat(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(created_by=user_id).order_by(cls.model.created_at.desc()).limit(1)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def final_name_for_chat(cls, user_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=user_id)

class ParticipantsDAO(BaseDAO):
    model = Participants

    
