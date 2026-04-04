from sqlalchemy import Column, Integer, String, Enum, Text
from sqlalchemy.orm import relationship

from database import Base
from Utils.Rarities import Rarities

class Mon(Base):
    __tablename__ = "mons"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    lvlfunc = Column(String(16), nullable=False, default="slow")
    rarity = Column(Enum(Rarities), default=Rarities.RARE)
    basehp = Column(Integer, default=20)
    basestr = Column(Integer, default=20)
    basedex = Column(Integer, default=20)
    basearc = Column(Integer, default=20)
    basefth = Column(Integer, default=20)
    baseadp = Column(Integer, default=20)
    baseexp = Column(Integer, default=40)

    instances = relationship("UserMon", back_populates="species")

    baseskills = relationship("Skill", back_populates="mons", secondary="monsskills")

    types = relationship("Type", back_populates="mons", secondary="monstypes")

    quests = relationship("Quest", back_populates="mons", secondary="questsmons")

    banners = relationship("Banner", back_populates="mons", secondary="bannersmons")

    battle_link = relationship("BattleParticipant", back_populates="mon")
