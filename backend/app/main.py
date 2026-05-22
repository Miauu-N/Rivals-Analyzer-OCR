from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.security import limiter
from app.core.database import engine, Base
import os

# Create DB tables
# In production, use Alembic instead.
from app.models import User, Upload, Match, Performance
Base.metadata.create_all(bind=engine)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(title=settings.PROJECT_NAME)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL], # Restricted from config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Rivals Replay Analyzer API"}

from app.routers import auth, uploads, matches, analytics
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
