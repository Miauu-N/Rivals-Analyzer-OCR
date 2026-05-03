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
                print(f"Error processing image {file_path}: {e}")
        
    return {"uploaded": saved_files}

@router.get("/")
def get_uploads(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    uploads = db.query(Upload).filter(Upload.user_id == current_user.id).all()
    return uploads
