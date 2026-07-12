import discord

from sqlalchemy import Column, Integer, String, Enum, BigInteger, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base
from Utils.Waifu import get_random_waifu_url
from Utils.Roles import Roles
from Utils.EventDispatcher import dispatch_event

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False, unique=True)
    role = Column(Enum(Roles), default=Roles.USER, nullable=False)
    sunlight = Column(Integer, default=100, nullable=False)
    lvl = Column(Integer, default=1)
    nextlvl = Column(Integer, default=1)
    birthday = Column(String(5), default="01/01")
    wimgurl = Column(String(512), default=lambda: get_random_waifu_url())
    msgcount = Column(Integer, default=0)

    quotes = relationship("Quote", back_populates="author")

    monuments = relationship("Monument", back_populates="users", secondary="usersmonuments")

    effect_links = relationship("EffectUser", back_populates="user")

    item_links = relationship("UserItem", back_populates="user")

    quest_links = relationship("UserQuest", back_populates="user")

    battle_link = relationship("BattleParticipant", back_populates="user")

    stocks = relationship("Stock", back_populates="owner") #stocks user created
    stock_portfolio = relationship("UserStock", back_populates="user") #stocks user bought

    mons = relationship("UserMon", back_populates="trainer")

    clan = relationship("Clan", back_populates="chairman", uselist=False)

    businesses = relationship("UserBusiness", back_populates="user")

    __table_args__ = (
        CheckConstraint("sunlight >= 0", name="check_sunlight_positive"),
        CheckConstraint("nextlvl > 0", name="check_nextlvl_gtzero")
    )

    def calc_nextlvl(self):
        self.nextlvl = int((4 * self.lvl**3) // 5)
    