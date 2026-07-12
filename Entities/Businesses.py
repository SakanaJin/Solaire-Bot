from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from Utils.Rarities import Rarities

class Business(Base):
    __tablename__ = "businesses"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    rarity = Column(Enum(Rarities), nullable=False, default=Rarities.COMMON)
    baserate = Column(Integer, nullable=False, default=20)
    lvlfunc = Column(String(16), nullable=False, default="slow")
    price = Column(Integer, nullable=False, default=200)

    typeid = Column(Integer, ForeignKey("businesstypes.id"))
    type = relationship("BusinessType", back_populates="businesses")

    areas = relationship("Area", back_populates="businesses", secondary="areasbusinesses")

    userbusinesses = relationship("UserBusiness", back_populates="business")