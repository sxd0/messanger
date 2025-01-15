from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    content: str = Field(description="Напишите что-то", min_length=1, max_length=300)