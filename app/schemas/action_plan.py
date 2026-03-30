from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ActionPlanBase(BaseModel):
    numero: int
    cv: int = 0
    zone: str
    non_conformite: str = Field(alias="nonConformite")
    cause: str
    action: str
    commentaires: str | None = None
    date_prevue: date | None = Field(default=None, alias="datePrevue")
    date_fin: date | None = Field(default=None, alias="dateFin")
    realisation: int = 0
    efficacite: str = "En cours"
    responsable: str

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("realisation")
    @classmethod
    def validate_realisation(cls, value: int) -> int:
        if value < 0 or value > 100:
            raise ValueError("Le pourcentage de realisation doit etre entre 0 et 100.")
        return value

    @field_validator("efficacite")
    @classmethod
    def normalize_efficacite(cls, value: str) -> str:
        cleaned = (value or "").strip()
        return cleaned or "En cours"


class ActionPlanCreate(ActionPlanBase):
    pass


class ActionPlanUpdate(ActionPlanBase):
    pass


class ActionPlan(ActionPlanBase):
    id: int
    created_at: datetime | None = Field(default=None, alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
