from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base

class UserBusiness(Base):
    __tablename__ = "userbusinesses"
    id = Column(Integer, primary_key=True)
    calcrate = Column(Integer, nullable=False)
    lvl = Column(Integer, nullable=False, default=1)
    nextlvl = Column(Integer, nullable=False, default=1)

    userid = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="businesses")

    businessid = Column(Integer, ForeignKey("businesses.id"))
    business = relationship("Business", back_populates="userbusinesses")

    managerid = Column(Integer, ForeignKey("clanmembers.id"))
    manager = relationship("ClanMember", back_populates="business", uselist=False)

    effect_links = relationship("EffectBusiness", back_populates="business")

