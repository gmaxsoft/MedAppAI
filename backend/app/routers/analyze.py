from typing import Any

from fastapi import APIRouter, Depends

from app.deps import get_current_doctor
from app.models import Doctor
from app.schemas.emg import AnalyzeEmgRequest, AnalyzeEmgResponse
from app.services.ai_service import generate_emg_description_sync
from app.services.anonymization import anonymize_for_llm
from app.services.norms import check_norms

router = APIRouter(tags=["analyze"])


@router.post("/analyze-emg", response_model=AnalyzeEmgResponse)
def analyze_emg(
    body: AnalyzeEmgRequest,
    _: Doctor = Depends(get_current_doctor),
) -> AnalyzeEmgResponse:
    nerve_dicts: list[dict[str, Any]] = [n.model_dump() for n in body.nerves]
    raw_data: dict[str, Any] = {
        "patient_id": body.patient_id,
        "norms": body.norms,
        "nerves": nerve_dicts,
        "muscles": body.muscles,
        "extra_context": body.extra_context,
    }

    default_norms = body.norms.get("default") if isinstance(body.norms.get("default"), dict) else {}
    deviations = check_norms(nerve_dicts, body.norms, default_norms=default_norms)

    technical_for_ai = anonymize_for_llm(
        {
            "norms": body.norms,
            "nerves": nerve_dicts,
            "muscles": body.muscles,
            "extra_context": body.extra_context,
        }
    )

    ai_text = generate_emg_description_sync(deviations, technical_for_ai)

    return AnalyzeEmgResponse(
        raw_data=raw_data,
        deviations=deviations,
        ai_description_draft=ai_text,
    )
