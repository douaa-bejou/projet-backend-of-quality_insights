from pydantic import BaseModel

class ActionPlanBase(BaseModel):
    pass

class ActionPlanCreate(ActionPlanBase):
    pass

class ActionPlan(ActionPlanBase):
    id: int

    class Config:
        from_attributes = True
