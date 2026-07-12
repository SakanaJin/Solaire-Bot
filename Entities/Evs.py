from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Evs(Base):
    __tablename__ = "evs"
    id = Column(Integer, ForeignKey("usersmons.id", ondelete="CASCADE"), primary_key=True)
    hp = Column(Integer, default=0)
    str = Column(Integer, default=0)
    dex = Column(Integer, default=0)
    arc = Column(Integer, default=0)
    fth = Column(Integer, default=0)
    adp = Column(Integer, default=0)

    mon = relationship("UserMon", back_populates="evs")