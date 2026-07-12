from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from database import Base

class TypeEffectiveness(Base):
    __tablename__ = "typeeffectiveness"
    atkid = Column(Integer, ForeignKey("types.id"), primary_key=True)
    defid = Column(Integer, ForeignKey("types.id"), primary_key=True)
    mult = Column(Float, nullable=False, default=1.0)

    attacker = relationship("Type", foreign_keys=[atkid], back_populates="atk_effectiveness")
    defender = relationship("Type", foreign_keys=[defid], back_populates="def_effectiveness")