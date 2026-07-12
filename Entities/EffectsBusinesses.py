from sqlalchemy import Integer, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class EffectBusiness(Base):
    __tablename__ = "effectsbusinesses"
    userbusinessid = Column(Integer, ForeignKey("userbusinesses.id"), primary_key=True)
    effectid = Column(Integer, ForeignKey("effects.id"), primary_key=True)
    expiresat = Column(DateTime(timezone=True), nullable=True, default=None)

    business = relationship("UserBusiness", back_populates="effect_links")
    effect = relationship("Effect", back_populates="business_links")
