from sqlalchemy import Column, Integer, BigInteger, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base

class UserMon(Base):
    __tablename__ = "usersmons"
    id = Column(Integer, primary_key=True)
    lvl = Column(Integer, default=1)
    nextlvl = Column(Integer, default=1)
    maxhp = Column(Integer, default=1)
    hp = Column(Integer, default=1)
    str = Column(Integer, default=1)
    dex = Column(Integer, default=1)
    arc = Column(Integer, default=1)
    fth = Column(Integer, default=1)
    adp = Column(Integer, default=1)
    ingaol = Column(Boolean, default=False)
    indungeon = Column(Boolean, default=False)
    inbattle = Column(Boolean, default=False)

    monid = Column(Integer, ForeignKey("mons.id"))
    species = relationship("Mon", back_populates="instances")

    trainerid = Column(BigInteger, ForeignKey("users.id"))
    trainer = relationship("User", back_populates="mons")

    ivs = relationship("Ivs", back_populates="mon", uselist=False, cascade="all, delete-orphan")
    evs = relationship("Evs", back_populates="mon", uselist=False, cascade="all, delete-orphan")

    skills = relationship("Skill", back_populates="usermons", secondary="usersmonsskills")

    effect_links = relationship("EffectUserMon", back_populates="mon")

    battle_link = relationship("BattleParticipant", back_populates="mon")

    __table_args__ = (
        CheckConstraint("hp > 0", name="check_hp_gtzero"),
        CheckConstraint("nextlvl > 0", name="check_nextlvl_gtzero")
    )