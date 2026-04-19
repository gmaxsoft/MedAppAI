from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_doctor
from app.models import Doctor, Examination, ExaminationStatus, Patient
from app.schemas.emg import ExaminationSaveRequest, ExaminationSaveResponse, ExaminationStatusEnum

router = APIRouter(prefix="/examinations", tags=["examinations"])


@router.post("/", response_model=ExaminationSaveResponse)
def save_examination(
    body: ExaminationSaveRequest,
    db: Session = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
) -> ExaminationSaveResponse:
    patient = db.query(Patient).filter(Patient.id == body.patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pacjent nie istnieje.")

    status_db = ExaminationStatus.approved if body.status == ExaminationStatusEnum.approved else ExaminationStatus.draft

    examination = Examination(
        patient_id=body.patient_id,
        doctor_id=doctor.id,
        raw_emg_data=body.raw_emg_data,
        norms_snapshot=body.norms_snapshot,
        ai_draft_description=None,
        final_description=body.final_description,
        status=status_db,
    )
    db.add(examination)
    db.commit()
    db.refresh(examination)

    return ExaminationSaveResponse(
        id=examination.id,
        patient_id=examination.patient_id,
        status=ExaminationStatusEnum(examination.status.value),
    )
