from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Business(Base):
    __tablename__ = "businesses"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    baserate = Column(Integer, nullable=False, default=20)
    lvlfunc = Column(String(16), nullable=False, default="slow")
    price = Column(Integer, nullable=False, default=200)

    typeid = Column(Integer, ForeignKey("businesstypes.id"))
    type = relationship("BusinessType", back_populates="businesses")

    areas = relationship("Area", back_populates="businesses", secondary="areasbusinesses")

    userbusiness = relationship("UserBusiness", back_populates="business")