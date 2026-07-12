from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from Utils.Rarities import Weights

class BannerYakuza(Base):
    __tablename__ = "bannersyakuza"
    bannerid = Column(Integer, ForeignKey("banners.id"), primary_key=True)
    yakuzaid = Column(Integer, ForeignKey("yakuza.id"), primary_key=True)
    weight = Column(Enum(Weights), nullable=False, default=Weights.COMMON)

    banner = relationship("Banner", back_populates="yakuza_links")
    yakuza = relationship("Yakuza", back_populates="banner_links")