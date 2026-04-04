from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class YakuzaEffects(Base):
    __tablename__ = "yakuzaeffects"
    yakuzaid = Column(Integer, ForeignKey("yakuza.id"), primary_key=True)
    effectid = Column(Integer, ForeignKey("effects.id"), primary_key=True)