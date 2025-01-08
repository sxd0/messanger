from sqlalchemy import select
from app.chats.models import Chats, Participants
from app.dao.base import BaseDAO
from app.database import async_session_maker


class ChatsDAO(BaseDAO): # Изучить
    model = Chats

    @classmethod
    async def add(cls, is_group: bool, created_by: int):
        async with async_session_maker() as session:
            new_chat = cls.model(is_group=is_group, created_by=created_by)
            session.add(new_chat)
            await session.commit()
            await session.refresh(new_chat)
            return new_chat.id


class ParticipantsDAO(BaseDAO):
    model = Participants

