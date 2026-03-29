from sqlalchemy.orm import Session

from app.models.quality_record import QualityRecord


def create_quality_record(db: Session, data: dict) -> QualityRecord:
    record = QualityRecord(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
