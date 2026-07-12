from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database import Base
from Utils.Rarities import Weights

class BannerItem(Base):
    __tablename__ = "bannersitems"
    bannerid = Column(Integer, ForeignKey("banners.id"), primary_key=True)
    itemid = Column(Integer, ForeignKey("items.id"), primary_key=True)
    weight = Column(Enum(Weights), nullable=False, default=Weights.COMMON)

    banner = relationship("Banner", back_populates="item_links")
    item = relationship("Item", back_populates="banner_links")