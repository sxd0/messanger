from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Boolean
from app.database import Base



class Chats(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    is_group = Column(Boolean, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)



class Participants(Base): # Участники чата
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
