import sys
import bcrypt

# Monkeypatch bcrypt.hashpw and checkpw to truncate passwords longer than 72 bytes.
# This prevents passlib from failing with "ValueError: password cannot be longer than 72 bytes"
# which happens in modern bcrypt versions (4.0.0+) during passlib initialization.
_original_hashpw = bcrypt.hashpw
def _patched_hashpw(password, salt):
    if isinstance(password, bytes) and len(password) > 72:
        password = password[:72]
    elif isinstance(password, str) and len(password.encode("utf-8")) > 72:
        password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return _original_hashpw(password, salt)
bcrypt.hashpw = _patched_hashpw

_original_checkpw = bcrypt.checkpw
def _patched_checkpw(password, hashed_password):
    if isinstance(password, bytes) and len(password) > 72:
        password = password[:72]
    elif isinstance(password, str) and len(password.encode("utf-8")) > 72:
        password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return _original_checkpw(password, hashed_password)
bcrypt.checkpw = _patched_checkpw


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import limiter

# Setup SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Disable the rate limiter during tests
limiter.enabled = False

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Re-create tables
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
