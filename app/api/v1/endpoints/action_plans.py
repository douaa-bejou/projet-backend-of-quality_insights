from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_current_user
from app.models import User


router = APIRouter(
    prefix="/action-plans",
    tags=["action-plans"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/")
def list_action_plans(current_user: User = Depends(get_current_user)):
    return {"items": [], "requested_by": current_user.email}


@router.post("/")
def create_action_plan(payload: dict, current_user: User = Depends(get_current_user)):
    return {"created": True, "payload": payload, "requested_by": current_user.email}
