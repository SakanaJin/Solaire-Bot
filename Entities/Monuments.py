from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base

class Monument(Base):
    __tablename__ = "monuments"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)

    users = relationship("User", back_populates="monuments", secondary="usersmonuments")

    quests = relationship("Quest", back_populates="monuments", secondary="questsmonuments")