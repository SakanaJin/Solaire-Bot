from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.orm import relationship

from database import Base
from Utils.Rarities import Rarities

class Area(Base):
    __tablename__ = "areas"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    rarity = Column(Enum(Rarities), default=Rarities.COMMON)
    familyprice = Column(Integer, nullable=False, default=1000)

    businesses = relationship("Business", back_populates="areas", secondary="areasbusinesses")