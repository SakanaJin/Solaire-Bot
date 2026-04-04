from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class BannerMon(Base):
    __tablename__ = "bannersmons"
    bannerid = Column(Integer, ForeignKey("banners.id"), primary_key=True)
    monid = Column(Integer, ForeignKey("mons.id"), primary_key=True)