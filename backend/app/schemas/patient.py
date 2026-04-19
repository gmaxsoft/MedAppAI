from pydantic import BaseModel, Field, field_validator


class PatientCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=128)
    last_name: str = Field(..., min_length=1, max_length=128)
    pesel: str | None = Field(None, min_length=11, max_length=11)
    notes: str | None = Field(None, max_length=5000)

    @field_validator("pesel")
    @classmethod
    def pesel_digits(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not v.isdigit():
            raise ValueError("PESEL musi składać się z 11 cyfr")
        return v


class PatientRead(BaseModel):
    id: int
    first_name: str
    last_name: str

    model_config = {"from_attributes": True}
