from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


PosteType = Literal["Moulage", "MQ100%", "MQ 200%", "Controle", "Maintenance"]
ShiftType = Literal["A", "B", "C"]
OriginType = Literal["R", "N"]


class QualityRecordBase(BaseModel):
    date: date
    semaine: int
    mois: str
    projet: str
    van: str
    shift: ShiftType
    designation: str
    poste: PosteType
    parts_origin: OriginType = Field(alias="partsOrigin")
    defaut: str | None = None
    photo_url: str | None = Field(default=None, alias="photoUrl")
    moulage_profil: str = Field(alias="moulageProfil")
    zone: str
    qte_ok: int = Field(0, alias="qteOk")
    qte_nok: int = Field(0, alias="qteNok")
    qte_nok_defaut: int = Field(0, alias="qteNokDefaut")
    qte_nok_moulage: int = Field(0, alias="qteNokMoulage")
    qte_nok_zone: int = Field(0, alias="qteNokZone")
    qte_scrap: int = Field(0, alias="qteScrap")
    qte_rework: int = Field(0, alias="qteRework")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "qte_ok",
        "qte_nok",
        "qte_nok_defaut",
        "qte_nok_moulage",
        "qte_nok_zone",
        "qte_scrap",
        "qte_rework",
    )
    @classmethod
    def validate_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Les quantites doivent etre >= 0.")
        return value


class QualityRecordCreate(QualityRecordBase):
    pass


class QualityRecordUpdate(QualityRecordBase):
    pass


class QualityRecord(QualityRecordBase):
    id: int
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
