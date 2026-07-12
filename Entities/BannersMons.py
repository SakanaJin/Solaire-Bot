from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database import Base
from Utils.Rarities import Weights

class BannerMon(Base):
    __tablename__ = "bannersmons"
    bannerid = Column(Integer, ForeignKey("banners.id"), primary_key=True)
    monid = Column(Integer, ForeignKey("mons.id"), primary_key=True)
    weight = Column(Enum(Weights), nullable=False, default=Weights.COMMON)

    banner = relationship("Banner", back_populates="mon_links")
    mon = relationship("Mon", back_populates="banner_links")