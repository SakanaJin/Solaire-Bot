from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from Utils.Affinities import Affinities

class Affinity(Base):
    __tablename__ = "affinities"
    businesstypeid = Column(Integer, ForeignKey("businesstypes.id"), primary_key=True)
    yakuzaid = Column(Integer, ForeignKey("yakuza.id"), primary_key=True)
    affinityval = Column(Enum(Affinities), default=Affinities.BAD)

    businesstype = relationship("BusinessType", back_populates="yakuza_links")
    yakuza = relationship("Yakuza", back_populates="affinity_links")