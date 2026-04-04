from sqlalchemy import Column, Integer, String, Enum, ForeignKey, BigInteger, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base
from Utils.FavorLevels import FavorLevels

class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    price = Column(Integer, nullable=False, default=3)
    favorlvl = Column(Enum(FavorLevels), default=FavorLevels.NEUTRAL)

    ownerid = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="stocks")

    investors = relationship("UserStock", back_populates="stock")

    effect_links = relationship("EffectStock", back_populates="stock")

    __table_args__ = (
        CheckConstraint("price > 0", name="check_price_gtzero"),
    )