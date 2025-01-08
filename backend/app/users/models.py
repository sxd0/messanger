from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    chats = relationship("Participants", back_populates="user")
    messages = relationship("Messages", back_populates="sender")