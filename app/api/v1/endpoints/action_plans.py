from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_current_user, get_db
from app.models import ActionPlan as ActionPlanModel, User
from app.schemas.action_plan import ActionPlan, ActionPlanCreate, ActionPlanUpdate


router = APIRouter(
    prefix="/action-plans",
    tags=["action-plans"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/")
def list_action_plans(
    q: str | None = Query(default=None, description="Recherche sur non-conformite/cause/action/zone/responsable."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ActionPlan]:
    query = select(ActionPlanModel)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(
            or_(
                ActionPlanModel.non_conformite.ilike(pattern),
                ActionPlanModel.cause.ilike(pattern),
                ActionPlanModel.action.ilike(pattern),
                ActionPlanModel.zone.ilike(pattern),
                ActionPlanModel.responsable.ilike(pattern),
                ActionPlanModel.commentaires.ilike(pattern),
            )
        )
    rows = db.execute(query.order_by(desc(ActionPlanModel.id))).scalars().all()
    return [ActionPlan.model_validate(row) for row in rows]


@router.post("/", response_model=ActionPlan, status_code=status.HTTP_201_CREATED)
def create_action_plan(
    payload: ActionPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActionPlan:
    row = ActionPlanModel(
        numero=payload.numero,
        cv=payload.cv,
        zone=payload.zone,
        non_conformite=payload.non_conformite,
        cause=payload.cause,
        action=payload.action,
        commentaires=payload.commentaires,
        date_prevue=payload.date_prevue,
        date_fin=payload.date_fin,
        realisation=payload.realisation,
        efficacite=payload.efficacite,
        responsable=payload.responsable,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ActionPlan.model_validate(row)


@router.put("/{action_plan_id}", response_model=ActionPlan)
def update_action_plan(
    action_plan_id: int,
    payload: ActionPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActionPlan:
    row = db.execute(select(ActionPlanModel).where(ActionPlanModel.id == action_plan_id)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action introuvable.")

    row.numero = payload.numero
    row.cv = payload.cv
    row.zone = payload.zone
    row.non_conformite = payload.non_conformite
    row.cause = payload.cause
    row.action = payload.action
    row.commentaires = payload.commentaires
    row.date_prevue = payload.date_prevue
    row.date_fin = payload.date_fin
    row.realisation = payload.realisation
    row.efficacite = payload.efficacite
    row.responsable = payload.responsable

    db.add(row)
    db.commit()
    db.refresh(row)
    return ActionPlan.model_validate(row)


@router.delete("/{action_plan_id}")
def delete_action_plan(
    action_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, bool | int]:
    row = db.execute(select(ActionPlanModel).where(ActionPlanModel.id == action_plan_id)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action introuvable.")
    db.delete(row)
    db.commit()
    return {"deleted": True, "id": action_plan_id}
