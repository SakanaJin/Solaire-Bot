from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class Type(Base):
    __tablename__ = "types"
    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False, unique=True)

    atk_effectiveness = relationship(
        "TypeEffectiveness", 
        foreign_keys="TypeEffectiveness.atkid",
        back_populates="attacker"
    )

    def_effectiveness = relationship(
        "TypeEffectiveness",
        foreign_keys="TypeEffectiveness.defid",
        back_populates="defender"
    )

    mons = relationship("Mon", back_populates="types", secondary="monstypes")