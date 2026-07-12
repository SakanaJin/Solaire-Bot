from sqlalchemy import Column, Integer, String, Text, Enum, CheckConstraint, Boolean
from sqlalchemy.orm import relationship
from enum import Enum as enoom

from database import Base

class EffectType(str, enoom):
    USER = "user"
    STOCK = "stock"
    MON = "mon"
    BUISINESS = "business"

class Effect(Base):
    __tablename__ = "effects"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    etype = Column(Enum(EffectType), nullable=False, default=EffectType.USER)
    value = Column(Integer, default=0)
    expiresin = Column(Integer, default=0)
    ispercent = Column(Boolean, default=True)

    user_links = relationship("EffectUser", back_populates="effect")

    stock_links = relationship("EffectStock", back_populates="effect")

    mon_links = relationship("EffectUserMon", back_populates="effect")

    business_links = relationship("EffectBusiness", back_populates="effect")

    items = relationship("Item", back_populates="effects", secondary="itemseffects")

    skills = relationship("Skill", back_populates="effects", secondary="skillseffects")

    quests = relationship("Quest", back_populates="effects", secondary="questseffects")

    yakuza = relationship("Yakuza", back_populates="effects", secondary="yakuzaeffects")

    __table_args__ = (
        CheckConstraint("expiresin >= 0", name="check_expiresin_gtzero"),
        CheckConstraint("value >= 0", name="check_value_gtzero")
    )