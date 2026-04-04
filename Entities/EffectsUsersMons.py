from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class EffectUserMon(Base):
    __tablename__ = "effectsusersmons"
    monid = Column(Integer, ForeignKey("usersmons.id"), primary_key=True)
    effectid = Column(Integer, ForeignKey("effects.id"), primary_key=True)
    expiresin = Column(Integer, nullable=False, default=0) #this is num turns instead of the usaul dt

    mon = relationship("UserMon", back_populates="effect_links")
    effect = relationship("Effect", back_populates="mon_links")