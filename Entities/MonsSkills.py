from sqlalchemy import Column, Integer, ForeignKey

from database import Base

class MonSkill(Base):
    __tablename__ = "monsskills"
    monid = Column(Integer, ForeignKey("mons.id"), primary_key=True)
    skillid = Column(Integer, ForeignKey("skills.id"), primary_key=True)