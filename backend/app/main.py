from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.session import Base, SessionLocal, engine
from app.models import Doctor
from app.core.security import hash_password
from app.routers import analyze, auth, examinations, patients

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(Doctor).count() == 0 and settings.seed_doctor_email and settings.seed_doctor_password:
            doc = Doctor(
                email=settings.seed_doctor_email.lower().strip(),
                hashed_password=hash_password(settings.seed_doctor_password),
                full_name="Lekarz (seed)",
            )
            db.add(doc)
            db.commit()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan, redirect_slashes=False)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(examinations.router)
app.include_router(analyze.router)


@app.get("/health")
def health():
    return {"status": "ok"}
