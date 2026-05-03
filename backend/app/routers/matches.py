from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.match import Match
from app.schemas.match import Match as MatchSchema

router = APIRouter()

@router.get("/", response_model=List[MatchSchema])
def get_matches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    matches = db.query(Match).filter(Match.user_id == current_user.id).order_by(Match.created_at.desc()).all()
    return matches

@router.delete("/clear")
def clear_matches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Delete all matches for the current user
    db.query(Match).filter(Match.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Historial limpiado correctamente"}

@router.get("/recommended", response_model=List[MatchSchema])
def get_recommended_matches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    matches = db.query(Match).filter(
        Match.user_id == current_user.id
    ).order_by(Match.replay_score.desc()).limit(5).all()
    return matches

@router.get("/{match_id}", response_model=MatchSchema)
def get_match(match_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    match = db.query(Match).filter(Match.id == match_id, Match.user_id == current_user.id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match
