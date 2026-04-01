from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import cast, desc, func, or_, select, String
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, get_db
from app.models import NonConformity as NonConformityModel, User
from app.schemas import NonConformity, NonConformityCreate, NonConformityUpdate


router = APIRouter(
    prefix="/non-conformities",
    tags=["non-conformities"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/")
def list_non_conformities(
    q: str | None = Query(default=None, description="Recherche globale sur NC."),
    date_filter: date | None = Query(default=None, alias="date"),
    semaine: int | None = None,
    mois: str | None = None,
    designation: str | None = None,
    defaut: str | None = None,
    poste: str | None = None,
    statut: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NonConformity]:
    query = select(NonConformityModel)

    if date_filter is not None:
        query = query.where(NonConformityModel.date == date_filter)
    if semaine is not None:
        query = query.where(NonConformityModel.semaine == semaine)
    if mois:
        query = query.where(NonConformityModel.mois == mois.strip())
    if designation:
        query = query.where(NonConformityModel.designation.ilike(f"%{designation.strip()}%"))
    if defaut:
        query = query.where(NonConformityModel.defaut.ilike(f"%{defaut.strip()}%"))
    if poste:
        query = query.where(NonConformityModel.poste == poste.strip())
    if statut:
        query = query.where(NonConformityModel.statut == statut.strip())
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(
            or_(
                cast(NonConformityModel.numero, String).ilike(pattern),
                NonConformityModel.designation.ilike(pattern),
                NonConformityModel.defaut.ilike(pattern),
                NonConformityModel.zone.ilike(pattern),
                NonConformityModel.poste.ilike(pattern),
                NonConformityModel.responsable.ilike(pattern),
                NonConformityModel.statut.ilike(pattern),
                NonConformityModel.priorite.ilike(pattern),
                NonConformityModel.commentaires.ilike(pattern),
                NonConformityModel.action_plan_ref.ilike(pattern),
            )
        )

    rows = db.execute(query.order_by(desc(NonConformityModel.created_at), desc(NonConformityModel.id))).scalars().all()
    return [NonConformity.model_validate(row) for row in rows]


@router.post("/", response_model=NonConformity, status_code=status.HTTP_201_CREATED)
def create_non_conformity(
    payload: NonConformityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NonConformity:
    max_numero = db.execute(select(func.max(NonConformityModel.numero))).scalar_one_or_none() or 0
    row = NonConformityModel(
        numero=int(max_numero) + 1,
        date=payload.date,
        semaine=payload.semaine,
        mois=payload.mois,
        designation=payload.designation.strip(),
        defaut=payload.defaut.strip(),
        qte_nok=payload.qte_nok,
        zone=payload.zone.strip(),
        poste=payload.poste.strip(),
        responsable=payload.responsable.strip(),
        statut=payload.statut,
        priorite=payload.priorite,
        date_echeance=payload.date_echeance,
        commentaires=payload.commentaires.strip(),
        action_plan_ref=payload.action_plan_ref.strip(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return NonConformity.model_validate(row)


@router.put("/{non_conformity_id}", response_model=NonConformity)
def update_non_conformity(
    non_conformity_id: int,
    payload: NonConformityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NonConformity:
    row = db.execute(select(NonConformityModel).where(NonConformityModel.id == non_conformity_id)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Non-conformite introuvable.")

    row.date = payload.date
    row.semaine = payload.semaine
    row.mois = payload.mois
    row.designation = payload.designation.strip()
    row.defaut = payload.defaut.strip()
    row.qte_nok = payload.qte_nok
    row.zone = payload.zone.strip()
    row.poste = payload.poste.strip()
    row.responsable = payload.responsable.strip()
    row.statut = payload.statut
    row.priorite = payload.priorite
    row.date_echeance = payload.date_echeance
    row.commentaires = payload.commentaires.strip()
    row.action_plan_ref = payload.action_plan_ref.strip()

    db.add(row)
    db.commit()
    db.refresh(row)
    return NonConformity.model_validate(row)


@router.delete("/{non_conformity_id}")
def delete_non_conformity(
    non_conformity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, bool | int]:
    row = db.execute(select(NonConformityModel).where(NonConformityModel.id == non_conformity_id)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Non-conformite introuvable.")
    db.delete(row)
    db.commit()
    return {"deleted": True, "id": non_conformity_id}

