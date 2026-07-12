from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)

    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="quotes")

