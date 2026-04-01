from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


NonConformityStatus = Literal["Ouverte", "En cours", "Cloturee"]
NonConformityPriority = Literal["Haute", "Moyenne", "Basse"]


class NonConformityBase(BaseModel):
    date: date
    semaine: int
    mois: str
    designation: str
    defaut: str
    qte_nok: int = Field(0, alias="qteNok")
    zone: str = ""
    poste: str
    responsable: str
    statut: NonConformityStatus = "Ouverte"
    priorite: NonConformityPriority = "Moyenne"
    date_echeance: date | None = Field(default=None, alias="dateEcheance")
    commentaires: str = ""
    action_plan_ref: str = Field(default="", alias="actionPlanRef")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("qte_nok")
    @classmethod
    def validate_non_negative_qte_nok(cls, value: int) -> int:
        if value < 0:
            raise ValueError("QTE NOK doit etre >= 0.")
        return value


class NonConformityCreate(NonConformityBase):
    pass


class NonConformityUpdate(NonConformityBase):
    pass


class NonConformity(NonConformityBase):
    id: int
    numero: int
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

