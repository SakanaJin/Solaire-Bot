from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database import Base
from Utils.Rarities import Weights

class AreaFish(Base):
    __tablename__ = "areasfish"
    fishid = Column(Integer, ForeignKey("items.id"), primary_key=True)
    areaid = Column(Integer, ForeignKey("areas.id"), primary_key=True)
    weight = Column(Enum(Weights), nullable=False, default=Weights.COMMON)

    fish = relationship("Item", back_populates="area_links")
    area = relationship("Area", back_populates="fish_links")
