from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.match import Match
from app.models.performance import Performance

router = APIRouter()

@router.get("/summary")
def get_stats_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_matches = db.query(Match).filter(Match.user_id == current_user.id).count()

    if total_matches == 0:
        return {
            "total_matches": 0,
            "win_rate": "0%",
            "avg_kda": "0.0",
            "top_heroes": []
        }

    wins = db.query(Match).filter(
        Match.user_id == current_user.id,
        Match.result.in_(["Victory", "Win", "WIN", "VICTORY", "VICTORY!"])
    ).count()
    
    win_rate_val = (wins / total_matches) * 100
    win_rate = f"{win_rate_val:.1f}%"

    user_performances = db.query(Performance).join(Match).filter(
        Match.user_id == current_user.id,
        Performance.is_main_user == True
    ).all()

    total_kills = sum(p.kills for p in user_performances if p.kills is not None)
    total_deaths = sum(p.deaths for p in user_performances if p.deaths is not None)
    total_assists = sum(p.assists for p in user_performances if p.assists is not None)

    if total_deaths == 0:
        if total_kills > 0 or total_assists > 0:
            avg_kda = "Perfect"
        else:
            avg_kda = "0.0"
    else:
        kda_ratio = (total_kills + total_assists) / total_deaths
        avg_kda = f"{kda_ratio:.2f}"

    role_counts = {}
    for p in user_performances:
        if p.role:
            role_counts[p.role] = role_counts.get(p.role, 0) + 1
    
    top_roles_sorted = sorted(role_counts.items(), key=lambda x: x[1], reverse=True)
    top_roles = [r[0] for r in top_roles_sorted[:3]]

    return {
        "total_matches": total_matches,
        "win_rate": win_rate,
        "avg_kda": avg_kda,
        "top_roles": top_roles
    }
