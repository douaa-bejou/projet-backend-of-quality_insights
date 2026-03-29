from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_current_user
from app.models import User


router = APIRouter(
    prefix="/quality-records",
    tags=["quality-records"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/")
def list_quality_records(current_user: User = Depends(get_current_user)):
    return {"items": [], "requested_by": current_user.email}


@router.post("/")
def create_quality_record(payload: dict, current_user: User = Depends(get_current_user)):
    return {"created": True, "payload": payload, "requested_by": current_user.email}
