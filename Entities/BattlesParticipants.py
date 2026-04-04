from sqlalchemy import Column, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class BattleParticipant(Base):
    __tablename__ = "battlesparticipants"
    battleid = Column(Integer, ForeignKey("battles.id"), primary_key=True)
    battle = relationship("Battle", back_populates="participants")
    slot = Column(Integer, default=0) #0 or 1

    userid = Column(BigInteger, ForeignKey("users.id"))
    user = relationship("User", back_populates="battle_link", uselist=False)
    
    monid = Column(Integer, ForeignKey("usersmons.id"))
    mon = relationship("UserMon", back_populates="battle_link", uselist=False)