from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import Doctor
from app.schemas.auth import DoctorCreate, DoctorRead, LoginRequest, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=DoctorRead)
def register(body: DoctorCreate, db: Session = Depends(get_db)) -> Doctor:
    settings = get_settings()
    if not settings.allow_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rejestracja jest wyłączona (ustaw ALLOW_REGISTRATION=true przy pierwszym uruchomieniu).",
        )
    if db.query(Doctor).filter(Doctor.email == str(body.email)).first():
        raise HTTPException(status_code=400, detail="Konto z tym adresem e-mail już istnieje.")
    doctor = Doctor(
        email=str(body.email).lower(),
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> Token:
    doctor = db.query(Doctor).filter(Doctor.email == str(body.email).lower()).first()
    if not doctor or not verify_password(body.password, doctor.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nieprawidłowe dane logowania.")
    token = create_access_token(subject=doctor.email)
    return Token(access_token=token)
