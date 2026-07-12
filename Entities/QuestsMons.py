from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class QuestMon(Base):
    __tablename__ = "questsmons"
    questid = Column(Integer, ForeignKey("quests.id"), primary_key=True)
    monid = Column(Integer, ForeignKey("mons.id"), primary_key=True)