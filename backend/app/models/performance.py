from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Performance(Base):
    __tablename__ = "performances"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    hero_name = Column(String)
    damage = Column(Integer)
    healing = Column(Integer)
    kills = Column(Integer)
    assists = Column(Integer)
    deaths = Column(Integer)
    mitigation = Column(Integer, nullable=True)

    match = relationship("Match", back_populates="performances")
