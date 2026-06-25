from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Performance(Base):
    __tablename__ = "performances"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    player_name = Column(String)
    team = Column(String, nullable=True)
    is_main_user = Column(Boolean, default=False)
    role = Column(String)
    damage = Column(Integer)
    healing = Column(Integer)
    kills = Column(Integer)
    assists = Column(Integer)
    deaths = Column(Integer)
    mitigation = Column(Integer, nullable=True)

    match = relationship("Match", back_populates="performances")
