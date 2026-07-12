from sqlalchemy import Integer, BigInteger, ForeignKey, CheckConstraint, Column
from sqlalchemy.orm import relationship

from database import Base

class UserStock(Base):
    __tablename__ = "usersstocks"
    userid = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    stockid = Column(Integer, ForeignKey("stocks.id"), primary_key=True)
    amount = Column(Integer, nullable=False, default=1)

    user = relationship("User", back_populates="stock_portfolio")
    stock = relationship("Stock", back_populates="investors")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_amount_gtzero"),
    )