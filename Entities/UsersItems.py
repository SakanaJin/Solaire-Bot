from sqlalchemy import Column, Integer, BigInteger, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base

class UserItem(Base):
    __tablename__ = "usersitems"
    userid = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    itemid = Column(Integer, ForeignKey("items.id"), primary_key=True)
    amount = Column(Integer, nullable=False, default=1)

    user = relationship("User", back_populates="item_links")
    item = relationship("Item", back_populates="user_links")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_amount_gtzero"),
    )