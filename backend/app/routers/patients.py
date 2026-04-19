from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_doctor
from app.models import Doctor, Patient
from app.schemas.patient import PatientCreate, PatientRead

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=list[PatientRead])
def list_patients(
    db: Session = Depends(get_db),
    _: Doctor = Depends(get_current_doctor),
) -> list[Patient]:
    return db.query(Patient).order_by(Patient.id.desc()).limit(200).all()


@router.post("", response_model=PatientRead)
def create_patient(
    body: PatientCreate,
    db: Session = Depends(get_db),
    _: Doctor = Depends(get_current_doctor),
) -> Patient:
    patient = Patient(
        first_name=body.first_name.strip(),
        last_name=body.last_name.strip(),
        pesel=body.pesel,
        notes=body.notes,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient
