from sqlalchemy import Integer, Column, ForeignKey

from database import Base

class SkillEffect(Base):
    __tablename__ = "skillseffects"
    skillid = Column(Integer, ForeignKey("skills.id"), primary_key=True)
    effectid = Column(Integer, ForeignKey("effects.id"), primary_key=True)