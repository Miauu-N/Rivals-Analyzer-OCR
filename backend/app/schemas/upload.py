from pydantic import BaseModel
from datetime import datetime

class UploadBase(BaseModel):
    image_type: str

class UploadCreate(UploadBase):
    image_path: str

class Upload(UploadBase):
    id: int
    user_id: int
    image_path: str
    processed: bool
    created_at: datetime

    class Config:
        from_attributes = True
