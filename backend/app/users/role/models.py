from sqlalchemy import ARRAY, Boolean, Column, Date, ForeignKey, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)

    users = relationship("Users", back_populates="role")