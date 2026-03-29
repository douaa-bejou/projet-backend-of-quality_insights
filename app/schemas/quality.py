from pydantic import BaseModel

class QualityRecordBase(BaseModel):
    pass

class QualityRecordCreate(QualityRecordBase):
    pass

class QualityRecord(QualityRecordBase):
    id: int

    class Config:
        from_attributes = True
