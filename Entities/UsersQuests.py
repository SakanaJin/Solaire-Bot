from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class UserQuest(Base):
    __tablename__ = "usersquests"
    userid = Column(Integer, ForeignKey("users.id"), primary_key=True)
    questid = Column(Integer, ForeignKey("quests.id"), primary_key=True)
    progress = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), default=None)

    user = relationship("User", back_populates="quest_links")
    quest = relationship("Quest", back_populates="user_links")
