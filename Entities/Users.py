from sqlalchemy import Column, Integer, String, Enum

from database import Base
from Utils.Roles import Roles

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    role = Column(Enum(Roles), default=Roles.USER, nullable=False)
