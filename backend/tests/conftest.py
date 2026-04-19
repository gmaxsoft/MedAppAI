"""Konfiguracja testów — zmienne środowiska przed importem aplikacji."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-jwt-tests-min-32-chars!")
os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("SEED_DOCTOR_EMAIL", "")
os.environ.setdefault("SEED_DOCTOR_PASSWORD", "")
os.environ.setdefault("ALLOW_REGISTRATION", "false")

from app.core.config import get_settings

get_settings.cache_clear()

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password


@pytest.fixture(scope="session", autouse=True)
def plaintext_password_scheme() -> None:
    """Stabilne hasła w testach bez zależności od bcrypt (różnice wersji bcrypt / Python)."""
    import app.core.security as sec

    sec.pwd_context = CryptContext(schemes=["plaintext"])


from app.db.session import Base, SessionLocal, engine
from app.main import app
from app.models import Doctor, Examination, Patient


@pytest.fixture(scope="session", autouse=True)
def create_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def wipe_tables() -> Generator[None, None, None]:
    with SessionLocal() as s:
        s.query(Examination).delete()
        s.query(Patient).delete()
        s.query(Doctor).delete()
        s.commit()
    yield


@pytest.fixture
def client(create_schema: None) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def doctor_and_headers() -> tuple[Doctor, dict[str, str]]:
    with SessionLocal() as s:
        doc = Doctor(
            email="doctor@example.com",
            hashed_password=hash_password("haslo-testowe-123"),
            full_name="Test Lekarz",
        )
        s.add(doc)
        s.commit()
        s.refresh(doc)
        token = create_access_token(doc.email)
        headers = {"Authorization": f"Bearer {token}"}
        return doc, headers


@pytest.fixture
def db_session(create_schema: None) -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
