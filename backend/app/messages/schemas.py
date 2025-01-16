from typing import Optional
from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    content: str = Field(description="Напишите что-то", min_length=1, max_length=300)

class WebSocketMessage(BaseModel):
    chat_id: int = Field(description="ID чата")
    content: str = Field(description="Текст сообщения", min_length=1, max_length=300)
    sender_id: Optional[int] = Field(default=None, description="ID отправителя")
    sender_name: Optional[str] = Field(default=None, description="Имя отправителя")