from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class BusinessType(Base):
    __tablename__ = "businesstypes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    yakuza_links = relationship("Affinity", back_populates="businesstype")

    businesses = relationship("Business", back_populates="type")