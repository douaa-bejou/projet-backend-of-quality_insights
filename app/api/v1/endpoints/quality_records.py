from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, get_db
from app.models import QualityRecord as QualityRecordModel, User
from app.schemas import QualityRecord, QualityRecordCreate, QualityRecordUpdate


router = APIRouter(
    prefix="/quality-records",
    tags=["quality-records"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/")
def list_quality_records(
    date_filter: date | None = Query(default=None, alias="date"),
    semaine: int | None = None,
    mois: str | None = None,
    projet: str | None = None,
    shift: str | None = None,
    poste: str | None = None,
    parts_origin: str | None = Query(default=None, alias="partsOrigin"),
    designation: str | None = None,
    defaut: str | None = None,
    zone: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[QualityRecord]:
    query = select(QualityRecordModel)

    if date_filter is not None:
        query = query.where(QualityRecordModel.date == date_filter)
    if semaine is not None:
        query = query.where(QualityRecordModel.semaine == semaine)
    if mois:
        query = query.where(QualityRecordModel.mois == mois.strip())
    if projet:
        query = query.where(QualityRecordModel.projet == projet.strip())
    if shift:
        query = query.where(QualityRecordModel.shift == shift.strip())
    if poste:
        query = query.where(QualityRecordModel.poste == poste.strip())
    if parts_origin:
        normalized_parts_origin = parts_origin.strip().upper()
        if normalized_parts_origin == "N":
            # Legacy rows may contain blank/null parts_origin for end-shift entries.
            # Treat them as "N" when the user explicitly filters on N.
            query = query.where(
                or_(
                    QualityRecordModel.parts_origin == "N",
                    QualityRecordModel.parts_origin == "",
                    QualityRecordModel.parts_origin.is_(None),
                )
            )
        else:
            query = query.where(QualityRecordModel.parts_origin == normalized_parts_origin)
    if designation:
        query = query.where(QualityRecordModel.designation.ilike(f"%{designation.strip()}%"))
    if defaut:
        query = query.where(QualityRecordModel.defaut.ilike(f"%{defaut.strip()}%"))
    if zone:
        query = query.where(QualityRecordModel.zone.ilike(f"%{zone.strip()}%"))

    records = db.execute(query.order_by(desc(QualityRecordModel.created_at), desc(QualityRecordModel.id))).scalars().all()
    return [QualityRecord.model_validate(record) for record in records]


@router.post("/", response_model=QualityRecord, status_code=status.HTTP_201_CREATED)
def create_quality_record(
    payload: QualityRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QualityRecord:
    record = QualityRecordModel(
        date=payload.date,
        semaine=payload.semaine,
        mois=payload.mois,
        projet=payload.projet,
        van=payload.van,
        shift=payload.shift,
        designation=payload.designation,
        poste=payload.poste,
        parts_origin=payload.parts_origin,
        defaut=payload.defaut,
        moulage_profil=payload.moulage_profil,
        zone=payload.zone,
        qte_ok=payload.qte_ok,
        qte_nok=payload.qte_nok,
        qte_scrap=payload.qte_scrap,
        qte_rework=payload.qte_rework,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return QualityRecord.model_validate(record)


@router.put("/{record_id}", response_model=QualityRecord)
def update_quality_record(
    record_id: int,
    payload: QualityRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> QualityRecord:
    record = db.execute(select(QualityRecordModel).where(QualityRecordModel.id == record_id)).scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enregistrement introuvable.")

    record.date = payload.date
    record.semaine = payload.semaine
    record.mois = payload.mois
    record.projet = payload.projet
    record.van = payload.van
    record.shift = payload.shift
    record.designation = payload.designation
    record.poste = payload.poste
    record.parts_origin = payload.parts_origin
    record.defaut = payload.defaut
    record.moulage_profil = payload.moulage_profil
    record.zone = payload.zone
    record.qte_ok = payload.qte_ok
    record.qte_nok = payload.qte_nok
    record.qte_scrap = payload.qte_scrap
    record.qte_rework = payload.qte_rework

    # When editing an end-shift entry, keep N/R lines consistent for the same shift group.
    is_end_shift_update = (payload.qte_ok + payload.qte_scrap + payload.qte_rework) > 0
    if is_end_shift_update:
        related_end_rows = db.execute(
            select(QualityRecordModel).where(
                QualityRecordModel.date == record.date,
                QualityRecordModel.projet == record.projet,
                QualityRecordModel.shift == record.shift,
                QualityRecordModel.designation == record.designation,
                (QualityRecordModel.qte_ok + QualityRecordModel.qte_scrap + QualityRecordModel.qte_rework) > 0,
            )
        ).scalars().all()

        for related in related_end_rows:
            related.date = record.date
            related.semaine = record.semaine
            related.mois = record.mois
            related.projet = record.projet
            related.van = record.van
            related.shift = record.shift
            related.designation = record.designation
            related.qte_ok = record.qte_ok
            related.qte_nok = 0
            related.qte_scrap = record.qte_scrap
            related.qte_rework = record.qte_rework

    db.add(record)
    db.commit()
    db.refresh(record)
    return QualityRecord.model_validate(record)


@router.delete("/{record_id}")
def delete_quality_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, bool | int]:
    record = db.execute(select(QualityRecordModel).where(QualityRecordModel.id == record_id)).scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enregistrement introuvable.")

    db.delete(record)
    db.commit()
    return {"deleted": True, "id": record_id}
