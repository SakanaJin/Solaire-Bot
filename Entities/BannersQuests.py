from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class BannerQuest(Base):
    __tablename__ = "bannersquests"
    bannerid = Column(Integer, ForeignKey("banners.id"), primary_key=True)
    questid = Column(Integer, ForeignKey("quests.id"), primary_key=True)