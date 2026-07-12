from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from Utils.Rarities import Weights

class BannerSkill(Base):
    __tablename__ = "bannersskills"
    bannerid = Column(Integer, ForeignKey("banners.id"), primary_key=True)
    skillid = Column(Integer, ForeignKey("skills.id"), primary_key=True)
    weight = Column(Enum(Weights), nullable=False, default=Weights.COMMON)

    banner = relationship("Banner", back_populates="skill_links")
    skill = relationship("Skill", back_populates="banner_links")