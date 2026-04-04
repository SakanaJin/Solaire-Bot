from sqlalchemy import Column, Integer, ForeignKey, BigInteger

from database import Base

class UserMonument(Base):
    __tablename__ = "usersmonuments"
    userid = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    monumentid = Column(Integer, ForeignKey("monuments.id"), primary_key=True)