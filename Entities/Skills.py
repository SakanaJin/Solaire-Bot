from sqlalchemy import Column, Integer, String, Text, Enum, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base
from Utils.Rarities import Rarities

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    rarity = Column(Enum(Rarities), default=Rarities.COMMON)
    basedmg = Column(Integer, nullable=False, default=1)

    scaling = relationship("Scaling", back_populates="skill", uselist=False, cascade="all, delete-orphan")

    effects = relationship("Effect", back_populates="skills", secondary="skillseffects")

    mons = relationship("Mon", back_populates="baseskills", secondary="monsskills")

    usermons = relationship("UserMon", back_populates="skills", secondary="usersmonsskills")

    banner_links = relationship("BannerSkill", back_populates="skill")

    __table_args__ = (
        CheckConstraint("basedmg > 0", name="check_basedmg_gtzero"),
    )