from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.orm import relationship

from database import Base
from Utils.Rarities import Rarities

class Banner(Base):
    __tablename__ = "banners"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    rarity = Column(Enum(Rarities), default=Rarities.COMMON)

    mon_links = relationship("BannerMon", back_populates="banner")

    item_links = relationship("BannerItem", back_populates="banner")

    yakuza_links = relationship("BannerYakuza", back_populates="banner")

    skill_links = relationship("BannerSkill", back_populates="banner")

    quests = relationship("Quest", back_populates="banners", secondary="bannersquests")