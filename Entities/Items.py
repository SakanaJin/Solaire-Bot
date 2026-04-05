from sqlalchemy import Column, Integer, String, Text, Enum, CheckConstraint, Boolean
from sqlalchemy.orm import relationship

from database import Base
from Utils.Rarities import Rarities

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    rarity = Column(Enum(Rarities), default=Rarities.COMMON)
    value = Column(Integer, nullable=False, default=0)
    equipable = Column(Boolean, default=False)
    nonbattleonly = Column(Boolean, default=True)
    useable = Column(Boolean, default=True)
    isfish = Column(Boolean, default=False)

    user_links = relationship("UserItem", back_populates="item")

    effects = relationship("Effect", back_populates="items", secondary="itemseffects")

    shop = relationship("ShopItem", back_populates="item", uselist=False, cascade="all, delete-orphan")

    quest_links = relationship("QuestItem", back_populates="item")

    banners = relationship("Banner", back_populates="items", secondary="bannersitems")

    __table_args__ = (
        CheckConstraint("value >= 0", name="check_value_positive"),
    )