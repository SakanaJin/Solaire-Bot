from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class BannerItem(Base):
    __tablename__ = "bannersitems"
    bannerid = Column(Integer, ForeignKey("banners.id"), primary_key=True)
    itemid = Column(Integer, ForeignKey("items.id"), primary_key=True)