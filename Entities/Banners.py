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

    mons = relationship("Mon", back_populates="banners", secondary="bannersmons")

    items = relationship("Item", back_populates="banners", secondary="bannersitems")

    quests = relationship("Quest", back_populates="banners", secondary="bannersquests")