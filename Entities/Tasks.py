from sqlalchemy import Column, Integer, String, Boolean

from database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    enabled = Column(Boolean, default=True)
