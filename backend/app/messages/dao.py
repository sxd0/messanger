import logging
from sqlalchemy import select
from app.dao.base import BaseDAO
from app.messages.models import Messages, Requests
from app.users.models import Users
from app.database import async_session_maker


logger = logging.getLogger(__name__)

class MessagesDAO(BaseDAO):
    model = Messages

    @classmethod
    async def find_all_with_senders(cls, chat_id: int):
        async with async_session_maker() as session:
            try:
                # Создаем запрос с join
                query = (
                    select(
                        cls.model.id,
                        cls.model.chat_id,
                        cls.model.sender_id,
                        cls.model.text,
                        Users.name.label("sender_name")
                    )
                    .join(Users, cls.model.sender_id == Users.id)
                    .where(cls.model.chat_id == chat_id)
                )
                result = await session.execute(query)
                return result.mappings().all()
            except Exception as e:
                logger.error(f"Error in find_all_with_senders: {str(e)}")
                raise ValueError(f"Database error: {str(e)}")

    


class RequestsDAO(BaseDAO):
    model = Requests
