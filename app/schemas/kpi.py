from pydantic import BaseModel

class KPICard(BaseModel):
    name: str
    value: float

class KPIResponse(BaseModel):
    items: list[KPICard]
