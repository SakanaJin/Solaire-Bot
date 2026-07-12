from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class ShopItem(Base):
    __tablename__ = "shopitems"
    itemid = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True)
    item = relationship("Item", back_populates="shop")