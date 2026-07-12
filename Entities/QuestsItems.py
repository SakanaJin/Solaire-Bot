from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base

class QuestItem(Base):
    __tablename__ = "questsitems"
    questid = Column(Integer, ForeignKey("quests.id"), primary_key=True)
    itemid = Column(Integer, ForeignKey("items.id"), primary_key=True)
    amount = Column(Integer, default=1)

    quest = relationship("Quest", back_populates="item_links")
    item = relationship("Item", back_populates="quest_links")