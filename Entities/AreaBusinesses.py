from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class AreaBusiness(Base):
    __tablename__ = "areasbusinesses"
    areaid = Column(Integer, ForeignKey("areas.id"), primary_key=True)
    businessid = Column(Integer, ForeignKey("businesses.id"), primary_key=True)