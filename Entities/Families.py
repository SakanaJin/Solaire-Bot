from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base

class Family(Base):
    __tablename__ = "families"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    lvl = Column(Integer, default=1)
    nextlvl = Column(Integer, default=1)
    lvlfunc = Column(String, nullable=False, default="Slow")

    clanid = Column(Integer, ForeignKey("clans.id"))
    clan = relationship("Clan", back_populates="families")

    areaid = Column(Integer, ForeignKey("areas.id"))
    area = relationship("Area", back_populates="families")

    members = relationship("ClanMember", back_populates="family")