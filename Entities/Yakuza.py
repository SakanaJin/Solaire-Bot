from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.orm import relationship

from database import Base
from Utils.Affinities import Proficiencies

class Yakuza(Base):
    __tablename__ = "yakuza"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    lvlfunc = Column(String(16), default="slow")
    baseproficiency = Column(Enum(Proficiencies), default=Proficiencies.BAD)

    effects = relationship("Effect", back_populates="yakuza", secondary="yakuzaeffects")

    affinity_links = relationship("Affinity", back_populates="yakuza")

    clans = relationship("ClanMember", back_populates="yakuza")