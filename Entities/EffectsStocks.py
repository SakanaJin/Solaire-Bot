from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class EffectStock(Base):
    __tablename__ = "effectsstocks"
    stockid = Column(Integer, ForeignKey("stocks.id"), primary_key=True)
    effectid = Column(Integer, ForeignKey("effects.id"), primary_key=True)
    expiresat = Column(DateTime(timezone=True))

    stock = relationship("Stock", back_populates="effect_links")
    effect = relationship("Effect", back_populates="stock_links")