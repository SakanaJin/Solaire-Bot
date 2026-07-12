from sqlalchemy import Column, Integer, Enum, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base
from Utils.Affinities import Proficiencies

class ClanMember(Base):
    __tablename__ = "clanmembers"
    id = Column(Integer, primary_key=True)
    lvl = Column(Integer, nullable=False, default=1)
    nextlvl = Column(Integer, nullable=False, default=1)
    proficiency = Column(Enum(Proficiencies), default=Proficiencies.BAD)

    yakuzaid = Column(Integer, ForeignKey("yakuza.id"))
    yakuza = relationship("Yakuza", back_populates="clans")

    clanid = Column(Integer, ForeignKey("clans.id"))
    clan = relationship("Clan", back_populates="members")

    familyid = Column(Integer, ForeignKey("families.id"))
    family = relationship("Family", back_populates="members")

    business = relationship("UserBusiness", back_populates="manager")

    __table_args__ = (
        CheckConstraint("lvl > 0", name="check_lvl_gtzero"),
        CheckConstraint("nextlvl > 0", name="check_nextlvl_gtzero")
    )
