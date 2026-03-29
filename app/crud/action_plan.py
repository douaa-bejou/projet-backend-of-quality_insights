from sqlalchemy.orm import Session

from app.models.action_plan import ActionPlan


def create_action_plan(db: Session, data: dict) -> ActionPlan:
    plan = ActionPlan(**data)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
