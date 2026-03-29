from pydantic import BaseModel

class FilterRequest(BaseModel):
    filters: dict = {}

class FilterResponse(BaseModel):
    items: list = []
