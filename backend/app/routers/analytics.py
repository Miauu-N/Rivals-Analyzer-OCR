from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/summary")
def get_stats_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Mock data for now
    return {
        "total_matches": 10,
        "win_rate": "60%",
        "avg_kda": "2.5",
        "top_heroes": ["Iron Man", "Spider-Man", "Hulk"]
    }
