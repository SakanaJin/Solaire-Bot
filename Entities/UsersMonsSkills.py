from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class UserMonSkill(Base):
    __tablename__ = "usersmonsskills"
    usermonid = Column(Integer, ForeignKey("usersmons.id"), primary_key=True)
    skillid = Column(Integer, ForeignKey("skills.id"), primary_key=True)