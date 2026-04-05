from sqlalchemy import Column, Integer, ForeignKey, DateTime, BigInteger, Boolean
from sqlalchemy.orm import relationship

from database import Base

class EffectUser(Base):
    __tablename__ = "effectsusers"
    userid = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    effectid = Column(Integer, ForeignKey("effects.id"), primary_key=True)
    expiresat = Column(DateTime(timezone=True))
    forsunlight = Column(Boolean, default=True)

    user = relationship("User", back_populates="effect_links")
    effect = relationship("Effect", back_populates="user_links")