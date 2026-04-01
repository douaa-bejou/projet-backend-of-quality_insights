from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.action_plans import router as action_plans_router
from app.api.v1.endpoints.quality_records import router as quality_records_router
from app.api.v1.endpoints.non_conformities import router as non_conformities_router

__all__ = ["auth_router", "action_plans_router", "quality_records_router", "non_conformities_router"]
