from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class QuestMonument(Base):
    __tablename__ = "questsmonuments"
    questid = Column(Integer, ForeignKey("quests.id"), primary_key=True)
    monumentid = Column(Integer, ForeignKey("monuments.id"), primary_key=True)