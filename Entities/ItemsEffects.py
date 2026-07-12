from sqlalchemy import Column, ForeignKey, Integer

from database import Base

class ItemEffect(Base):
    __tablename__ = "itemseffects"
    itemid = Column(Integer, ForeignKey("items.id"), primary_key=True)
    effectid = Column(Integer, ForeignKey("effects.id"), primary_key=True)