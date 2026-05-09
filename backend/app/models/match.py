from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    map_name = Column(String)
    result = Column(String) # 'Win' | 'Loss' | 'Draw'
    duration_seconds = Column(Integer)
    team_score = Column(Integer)
    enemy_score = Column(Integer)
    kda = Column(String)
    rank = Column(String)
    replay_id = Column(String)
    replay_score = Column(Float, default=0.0) # Used for recommendations
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="matches")
    performances = relationship("Performance", back_populates="match", cascade="all, delete-orphan")
