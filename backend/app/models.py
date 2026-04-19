import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ExaminationStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    examinations: Mapped[list["Examination"]] = relationship("Examination", back_populates="doctor")


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[str] = mapped_column(String(128))
    pesel: Mapped[str | None] = mapped_column(String(11), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    examinations: Mapped[list["Examination"]] = relationship("Examination", back_populates="patient")


class Examination(Base):
    __tablename__ = "examinations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[int | None] = mapped_column(ForeignKey("doctors.id"), nullable=True)

    raw_emg_data: Mapped[dict] = mapped_column(JSONB)
    norms_snapshot: Mapped[dict] = mapped_column(JSONB)
    ai_draft_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ExaminationStatus] = mapped_column(Enum(ExaminationStatus), default=ExaminationStatus.draft)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="examinations")
    doctor: Mapped["Doctor | None"] = relationship("Doctor", back_populates="examinations")
