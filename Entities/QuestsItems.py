from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class QuestItem(Base):
    __tablename__ = "questsitems"
    questid = Column(Integer, ForeignKey("quests.id"), primary_key=True)
    itemid = Column(Integer, ForeignKey("items.id"), primary_key=True)