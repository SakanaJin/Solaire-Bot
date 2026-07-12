from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, CheckConstraint, Boolean
from sqlalchemy.orm import relationship

from database import Base
from Utils.QuestConsts import QuestCategories, QuestTypes
from Utils.Rarities import Rarities

class Quest(Base):
    __tablename__ = "quests"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    rarity = Column(Enum(Rarities), default=Rarities.COMMON)
    type = Column(Enum(QuestTypes), default=QuestTypes.COMMAND) #kill, collect, lvl up, command
    category = Column(Enum(QuestCategories), default=QuestCategories.MAIN) #main, daily, banner
    target = Column(Integer, default=1)
    target_identifier = Column(String(256), nullable=False) #command name, mon name, item name
    sunlight = Column(Integer, default=0)
    exp = Column(Integer, default=0)
    expiresat = Column(DateTime(timezone=True), default=None)
    hidden = Column(Boolean, default=False)

    item_links = relationship("QuestItem", back_populates="quest")

    effects = relationship("Effect", back_populates="quests", secondary="questseffects")

    mons = relationship("Mon", back_populates="quests", secondary="questsmons")

    monuments = relationship("Monument", back_populates="quests", secondary="questsmonuments")

    banners = relationship("Banner", back_populates="quests", secondary="bannersquests")

    user_links = relationship("UserQuest", back_populates="quest")

    __table_args__ = (
        CheckConstraint("sunlight >= 0", name="check_sunlight_positive"),
        CheckConstraint("exp >= 0", name="check_exp_positive")
    )