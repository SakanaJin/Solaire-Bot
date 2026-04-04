from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class QuestEffect(Base):
    __tablename__ = "questseffects"
    questid = Column(Integer, ForeignKey("quests.id"), primary_key=True)
    effectid = Column(Integer, ForeignKey("effects.id"), primary_key=True)