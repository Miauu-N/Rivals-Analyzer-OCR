from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PerformanceBase(BaseModel):
    player_name: Optional[str] = None
    team: Optional[str] = None
    is_main_user: Optional[bool] = False
    hero_name: Optional[str] = None  # stores role: Vanguard / Duelist / Strategist
    damage: int
    healing: int
    kills: int
    assists: int
    deaths: int
    mitigation: Optional[int] = None

class PerformanceCreate(PerformanceBase):
    pass

class Performance(PerformanceBase):
    id: int
    match_id: int

    class Config:
        from_attributes = True

class MatchBase(BaseModel):
    map_name: Optional[str] = None
    result: Optional[str] = None
    duration_seconds: Optional[int] = None
    team_score: Optional[int] = None
    enemy_score: Optional[int] = None
    kda: Optional[str] = None
    rank: Optional[str] = None
    replay_id: Optional[str] = None
    replay_score: Optional[float] = 0.0

class MatchCreate(MatchBase):
    performances: List[PerformanceCreate] = []

class Match(MatchBase):
    id: int
    user_id: int
    created_at: datetime
    performances: List[Performance] = []

    class Config:
        from_attributes = True
