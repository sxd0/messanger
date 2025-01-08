from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Boolean
from app.database import Base
from sqlalchemy.orm import relationship


class Chats(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    is_group = Column(Boolean, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    participants = relationship("Participants", back_populates="chat")
    messages = relationship("Messages", back_populates="chat")


class Participants(Base): # Участники чата
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("Users", back_populates="chats")
    chat = relationship("Chats", back_populates="participants")