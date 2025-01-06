from datetime import datetime
from sqlalchemy import Column, Date, DateTime, Integer, String
from app.database import Base



class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
