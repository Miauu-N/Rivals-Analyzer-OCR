from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.upload import Upload
from app.core.config import settings
import os
import shutil
import uuid

router = APIRouter()

@router.post("/upload-images")
async def upload_images(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import asyncio
    from app.services.ocr.classifier import classify_image
    from app.services.ocr.history_parser import parse_history
    from app.services.ocr.scoreboard_parser import parse_scoreboard
    from app.services.ocr.scorer import calculate_replay_score
    from app.models.match import Match
    from app.models.performance import Performance
    from sqlalchemy import func
    import re

    saved_files = []
    uploads_to_process = []
    
    # PHASE 1: Save files to disk
    for file in files:
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        uploads_to_process.append({"file": file, "path": file_path, "ext": file_ext})
        
    # Run classification concurrently
    async def run_classification(item):
        img_type = await asyncio.to_thread(classify_image, item["path"])
        item["type"] = img_type
        return item
        
    classified_items = await asyncio.gather(*(run_classification(item) for item in uploads_to_process))
    
    db_uploads = []
    for item in classified_items:
        db_upload = Upload(
            user_id=current_user.id,
            image_path=item["path"],
            image_type=item["type"],
            processed=False
        )
        db.add(db_upload)
        db_uploads.append(db_upload)
        
    db.commit()
    for u in db_uploads:
        db.refresh(u)
        
    for i, item in enumerate(classified_items):
        item["upload_id"] = db_uploads[i].id
        saved_files.append({"id": db_uploads[i].id, "type": item["type"], "path": item["path"]})

    # PHASE 2: OCR Parsing concurrently
    async def run_parsing(item):
        result = None
        if item["type"] == "history":
            try:
                result = await asyncio.to_thread(parse_history, item["path"])
            except Exception as e:
                print(f"Error parsing history {item['path']}: {e}")
        elif item["type"] == "scoreboard":
            try:
                result = await asyncio.to_thread(parse_scoreboard, item["path"])
            except Exception as e:
                print(f"Error parsing scoreboard {item['path']}: {e}")
        item["ocr_result"] = result
        return item
        
    parsed_items = await asyncio.gather(*(run_parsing(item) for item in classified_items))

    # PHASE 3: Database Updates (Sequentially)
    DURATION_TOLERANCE = 60  # seconds
    
    def map_word_set(name: str) -> set:
        words = re.split(r"[\s\-'.,]+", (name or "").upper())
        return {w for w in words if len(w) >= 3}
        
    for item in parsed_items:
        db_upload = db.query(Upload).filter(Upload.id == item["upload_id"]).first()
        if not db_upload:
            continue
            
        if item["type"] == "history" and item.get("ocr_result"):
            extracted_matches = item["ocr_result"]
            for m_data in extracted_matches:
                replay_score = calculate_replay_score(m_data)
                
                hist_map = (m_data.get("map_name") or "").strip().upper()
                hist_result = (m_data.get("result") or "").strip().upper()
                hist_duration = m_data.get("duration_seconds") or 0
                
                existing_match = None
                if hist_map and hist_result and hist_duration:
                    candidates = db.query(Match).filter(
                        Match.user_id == current_user.id,
                        func.upper(Match.result) == hist_result,
                        Match.duration_seconds.between(
                            hist_duration - DURATION_TOLERANCE,
                            hist_duration + DURATION_TOLERANCE
                        )
                    ).all()
                    
                    hist_words = map_word_set(hist_map)
                    best_candidate = None
                    best_overlap = 0
                    
                    for candidate in candidates:
                        candidate_words = map_word_set(candidate.map_name)
                        overlap = len(hist_words & candidate_words)
                        if overlap > best_overlap:
                            best_overlap = overlap
                            best_candidate = candidate
                    
                    if best_candidate and best_overlap >= 2:
                        existing_match = best_candidate
                        
                if existing_match:
                    db_match = existing_match
                    if not db_match.rank and m_data.get("rank"):
                        db_match.rank = m_data.get("rank")
                    if not db_match.kda and m_data.get("kda"):
                        db_match.kda = m_data.get("kda")
                    if m_data.get("created_at"):
                        db_match.created_at = m_data.get("created_at")
                    print(f"Updated existing match ID {db_match.id} with history data")
                else:
                    db_match = Match(
                        user_id=current_user.id,
                        map_name=m_data.get("map_name"),
                        result=m_data.get("result"),
                        duration_seconds=m_data.get("duration_seconds"),
                        kda=m_data.get("kda"),
                        rank=m_data.get("rank"),
                        replay_score=replay_score
                    )
                    
                    if m_data.get("created_at"):
                        db_match.created_at = m_data.get("created_at")
                        
                    db.add(db_match)
                    print(f"Created new match from history, ID {db_match.id}")
            
            db_upload.processed = True
            db.commit()

        elif item["type"] == "scoreboard" and item.get("ocr_result"):
            data = item["ocr_result"]
            if data and "match_info" in data:
                match_info = data["match_info"]
                performances = data.get("performances", [])
                sb_map = (match_info.get("map_name") or "").strip().upper()
                sb_result = (match_info.get("result") or "").strip().upper()
                sb_duration = match_info.get("duration_seconds") or 0
                
                main_kda = None
                for p in performances:
                    if p.get("is_main_user"):
                        main_kda = f"{p.get('kills', 0)}/{p.get('deaths', 0)}/{p.get('assists', 0)}"
                        break
                
                existing_match = None
                if sb_map and sb_result and sb_duration:
                    candidates = db.query(Match).filter(
                        Match.user_id == current_user.id,
                        func.upper(Match.result) == sb_result,
                        Match.duration_seconds.between(
                            sb_duration - DURATION_TOLERANCE,
                            sb_duration + DURATION_TOLERANCE
                        )
                    ).all()
                    
                    sb_words = map_word_set(sb_map)
                    best_candidate = None
                    best_overlap = 0
                    
                    for candidate in candidates:
                        candidate_words = map_word_set(candidate.map_name or "")
                        overlap = len(sb_words & candidate_words)
                        if overlap > best_overlap:
                            best_overlap = overlap
                            best_candidate = candidate
                    
                    if best_candidate and best_overlap >= 2:
                        existing_match = best_candidate
                
                if existing_match:
                    db_match = existing_match
                    if not db_match.kda and main_kda:
                        db_match.kda = main_kda
                    if not db_match.replay_id and match_info.get("replay_id"):
                        db_match.replay_id = str(match_info.get("replay_id"))
                    print(f"Linked scoreboard to existing match ID {db_match.id}")
                else:
                    temp_score_data = {
                        "result": match_info.get("result"),
                        "duration_seconds": sb_duration
                    }
                    replay_score = calculate_replay_score(temp_score_data)
                    db_match = Match(
                        user_id=current_user.id,
                        map_name=match_info.get("map_name"),
                        result=match_info.get("result"),
                        duration_seconds=sb_duration,
                        kda=main_kda,
                        replay_id=str(match_info.get("replay_id")) if match_info.get("replay_id") else None,
                        replay_score=replay_score
                    )
                    db.add(db_match)
                    db.commit()
                    db.refresh(db_match)
                    print(f"Created new match from scoreboard, ID {db_match.id}")
                
                existing_perf_count = db.query(Performance).filter(
                    Performance.match_id == db_match.id
                ).count()
                
                if existing_perf_count == 0:
                    for p_data in performances:
                        perf = Performance(
                            match_id=db_match.id,
                            player_name=p_data.get("player_name"),
                            team=p_data.get("team"),
                            is_main_user=p_data.get("is_main_user", False),
                            role=p_data.get("role"),
                            damage=p_data.get("damage", 0),
                            healing=p_data.get("healing", 0),
                            kills=p_data.get("kills", 0),
                            assists=p_data.get("assists", 0),
                            deaths=p_data.get("deaths", 0),
                            mitigation=p_data.get("damage_blocked", 0)
                        )
                        db.add(perf)
                
                db_upload.processed = True
                db.commit()

    # Cleanup old uploads if there are more than 40
    user_uploads = db.query(Upload).filter(Upload.user_id == current_user.id).order_by(Upload.id.asc()).all()
    if len(user_uploads) > 40:
        uploads_to_delete = user_uploads[:-40]
        for old_upload in uploads_to_delete:
            if os.path.exists(old_upload.image_path):
                try:
                    os.remove(old_upload.image_path)
                except Exception as e:
                    print(f"Failed to delete file {old_upload.image_path}: {e}")
            db.delete(old_upload)
        db.commit()
        print(f"Cleaned up {len(uploads_to_delete)} old uploads for user {current_user.id}")
        
    return {"uploaded": saved_files}

@router.get("/")
def get_uploads(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    uploads = db.query(Upload).filter(Upload.user_id == current_user.id).all()
    return uploads
