from datetime import datetime
from sqlalchemy import ARRAY, Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship


class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(String, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chats", back_populates="messages")
    sender = relationship("Users", back_populates="messages")

class Requests(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(ARRAY(String), nullable=False) # принято/отклонено/в ожидании
