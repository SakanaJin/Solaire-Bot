from sqlalchemy import Column, Integer, String, Text, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Clan(Base):
    __tablename__ = "clans"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    lvl = Column(Integer, nullable=False, default=1)
    nextlvl = Column(Integer, nullable=False, default=1)

    chairmanid = Column(Integer, ForeignKey("users.id"))
    chairman = relationship("User", back_populates="Clan", uselist=False)

    families = relationship("Family", back_populates="clan")

    members = relationship("ClanMember", back_populates="clan")

    __table_args__ = (
        CheckConstraint("nextlvl > 0", name="check_nextlvl_gtzero"),
    )