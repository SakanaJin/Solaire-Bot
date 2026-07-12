from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class MonType(Base):
    __tablename__ = "monstypes"
    monid = Column(Integer, ForeignKey("mons.id"), primary_key=True)
    typeid = Column(Integer, ForeignKey("types.id"), primary_key=True)