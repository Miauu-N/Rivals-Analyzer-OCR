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
    saved_files = []
    for file in files:
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Determine image type and extract data via OCR
        # This will be connected to the OCR service
        from app.services.ocr.classifier import classify_image
        image_type = classify_image(file_path)
        
        db_upload = Upload(
            user_id=current_user.id,
            image_path=file_path,
            image_type=image_type,
            processed=False
        )
        db.add(db_upload)
        db.commit()
        db.refresh(db_upload)
        saved_files.append({"id": db_upload.id, "type": image_type, "path": file_path})
        
        # Trigger processing
        from app.services.ocr.history_parser import parse_history
        from app.services.ocr.scorer import calculate_replay_score
        from app.models.match import Match
        
        if image_type == "history":
            try:
                extracted_matches = parse_history(file_path)
                for m_data in extracted_matches:
                    replay_score = calculate_replay_score(m_data)
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
                
                db_upload.processed = True
                db.commit()
            except Exception as e:
                print(f"Error processing history image {file_path}: {e}")
                
        elif image_type == "scoreboard":
            from app.services.ocr.scoreboard_parser import parse_scoreboard
            from app.models.performance import Performance
            from sqlalchemy import func
            try:
                data = parse_scoreboard(file_path)
                if data and "match_info" in data:
                    match_info = data["match_info"]
                    performances = data.get("performances", [])
                    sb_map = (match_info.get("map_name") or "").strip().upper()
                    sb_result = (match_info.get("result") or "").strip().upper()
                    sb_duration = match_info.get("duration_seconds") or 0
                    
                    # Find main user KDA
                    main_kda = None
                    for p in performances:
                        if p.get("is_main_user"):
                            main_kda = f"{p.get('kills', 0)}/{p.get('deaths', 0)}/{p.get('assists', 0)}"
                            break
                    
                    # --- Try to find an existing match to link to ---
                    DURATION_TOLERANCE = 60  # seconds
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
                        
                        # Among candidates, pick the one whose map name is most similar.
                        # The scoreboard shows maps as "ZONE-SUBMAP" while history shows "Submap - Zone"
                        # so we normalize both to a bag of words and count overlap.
                        def map_word_set(name: str) -> set:
                            import re
                            # Split on spaces, dashes, apostrophes, dots — keep only words of 3+ chars
                            words = re.split(r"[\s\-'.,]+", name.upper())
                            return {w for w in words if len(w) >= 3}
                        
                        sb_words = map_word_set(sb_map)
                        best_candidate = None
                        best_overlap = 0
                        
                        for candidate in candidates:
                            candidate_words = map_word_set(candidate.map_name or "")
                            overlap = len(sb_words & candidate_words)
                            if overlap > best_overlap:
                                best_overlap = overlap
                                best_candidate = candidate
                        
                        # Require at least 2 words in common to consider it a match
                        if best_candidate and best_overlap >= 2:
                            existing_match = best_candidate
                    
                    if existing_match:
                        # Link performances to existing match and update KDA if missing
                        db_match = existing_match
                        if not db_match.kda and main_kda:
                            db_match.kda = main_kda
                        print(f"Linked scoreboard to existing match ID {db_match.id}")
                    else:
                        # Create a new match from the scoreboard data
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
                            replay_score=replay_score
                        )
                        db.add(db_match)
                        db.commit()
                        db.refresh(db_match)
                        print(f"Created new match from scoreboard, ID {db_match.id}")
                    
                    # Avoid duplicating performances if already linked
                    existing_perf_count = db.query(Performance).filter(
                        Performance.match_id == db_match.id
                    ).count()
                    
                    if existing_perf_count == 0:
                        for p_data in performances:
                            perf = Performance(
                                match_id=db_match.id,
                                player_name=p_data.get("player_name"),
                                is_main_user=p_data.get("is_main_user", False),
                                hero_name=p_data.get("hero_name"),
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
            except Exception as e:
                print(f"Error processing scoreboard image {file_path}: {e}")
        
    return {"uploaded": saved_files}

@router.get("/")
def get_uploads(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    uploads = db.query(Upload).filter(Upload.user_id == current_user.id).all()
    return uploads
