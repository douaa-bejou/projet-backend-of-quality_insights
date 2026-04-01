from fastapi import APIRouter

from app.api.v1.endpoints import action_plans_router, auth_router, non_conformities_router, quality_records_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(action_plans_router)
api_router.include_router(quality_records_router)
api_router.include_router(non_conformities_router)
