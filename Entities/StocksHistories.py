from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base

class StockHistory(Base):
    __tablename__ = "stockshistories"
    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    percentchange = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)

    stockid = Column(Integer, ForeignKey("stocks.id"))
    stock = relationship("Stock", back_populates="history")