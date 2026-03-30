from sqlalchemy import Column, Integer, String, Enum, BigInteger, CheckConstraint

from database import Base
from Utils.Roles import Roles

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    role = Column(Enum(Roles), default=Roles.USER, nullable=False)
    sunlight = Column(Integer, default=100, nullable=False)

    __table_args__ = (
        CheckConstraint("sunlight >= 0", name="check_sunlight_positive"),
    )
