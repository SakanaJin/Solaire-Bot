from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from Utils.Scales import Scales

class Scaling(Base):
    __tablename__ = "scalings"
    skillid = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    str = Column(Enum(Scales), nullable=False, default=Scales.NONE)
    dex = Column(Enum(Scales), nullable=False, default=Scales.NONE)
    arc = Column(Enum(Scales), nullable=False, default=Scales.NONE)
    fth = Column(Enum(Scales), nullable=False, default=Scales.NONE)
    adp = Column(Enum(Scales), nullable=False, default=Scales.NONE)
    
    skill = relationship("Skill", back_populates="scaling")