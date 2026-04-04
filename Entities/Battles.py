from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Battle(Base):
    __tablename__ = "battles"
    id = Column(Integer, primary_key=True)
    turn = Column(Integer, default=0)
    playerturn = Column(Integer, default=0) #0 or 1
    isboss = Column(Boolean, default=False)

    participants = relationship("BattleParticipant", back_populates="battle")