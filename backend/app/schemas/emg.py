from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ExaminationStatusEnum(str, Enum):
    draft = "draft"
    approved = "approved"


class NerveMeasurement(BaseModel):
    """Pomiary dla pojedynczego nerwu / ścieżki badania."""

    nerve_key: str = Field(..., min_length=1, max_length=128, description="Identyfikator nerwu, np. nerw_pośrodkowy")
    latency_ms: float | None = Field(None, ge=0, le=500, description="Latencja (ms)")
    amplitude_mv: float | None = Field(None, ge=0, le=100, description="Amplituda CMAP (mV)")
    f_wave_latency_ms: float | None = Field(None, ge=0, le=500, description="Latencja fali F (ms)")
    conduction_velocity_m_s: float | None = Field(None, ge=0, le=120, description="Szybkość przewodzenia (m/s)")
    notes: str | None = Field(None, max_length=2000)


class AnalyzeEmgRequest(BaseModel):
    patient_id: int | None = Field(None, ge=1)
    norms: dict[str, Any] = Field(default_factory=dict, description="Normy referencyjne wg nerwu i parametru")
    nerves: list[NerveMeasurement] = Field(..., min_length=1)
    muscles: dict[str, Any] = Field(default_factory=dict)
    extra_context: str | None = Field(None, max_length=5000)

    @field_validator("norms", mode="before")
    @classmethod
    def norms_must_be_mapping(cls, v: Any) -> dict[str, Any]:
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError("norms musi być obiektem JSON")
        return v


class AnalyzeEmgResponse(BaseModel):
    raw_data: dict[str, Any]
    deviations: list[dict[str, Any]]
    ai_description_draft: str


class ExaminationSaveRequest(BaseModel):
    patient_id: int = Field(..., ge=1)
    raw_emg_data: dict[str, Any]
    norms_snapshot: dict[str, Any]
    final_description: str = Field(..., min_length=1, max_length=50000)
    status: ExaminationStatusEnum = ExaminationStatusEnum.approved


class ExaminationSaveResponse(BaseModel):
    id: int
    patient_id: int
    status: ExaminationStatusEnum

    model_config = {"from_attributes": True}
