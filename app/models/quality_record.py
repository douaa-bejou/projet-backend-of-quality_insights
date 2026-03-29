from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class QualityRecord(Base):
    __tablename__ = "quality_records"
    __table_args__ = (
        CheckConstraint("qte_ok >= 0", name="ck_quality_records_qte_ok_non_negative"),
        CheckConstraint("qte_nok >= 0", name="ck_quality_records_qte_nok_non_negative"),
        CheckConstraint("qte_scrap >= 0", name="ck_quality_records_qte_scrap_non_negative"),
        CheckConstraint("qte_rework >= 0", name="ck_quality_records_qte_rework_non_negative"),
        Index("ix_quality_records_date_project_shift", "date", "projet", "shift"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    semaine: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    mois: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    projet: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    van: Mapped[str] = mapped_column(String(50), nullable=False)
    shift: Mapped[str] = mapped_column(String(1), nullable=False, index=True)
    designation: Mapped[str] = mapped_column(String(100), nullable=False)
    poste: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    parts_origin: Mapped[str] = mapped_column(String(1), nullable=False, index=True)
    defaut: Mapped[str | None] = mapped_column(String(100), nullable=True)
    moulage_profil: Mapped[str] = mapped_column(String(50), nullable=False)
    zone: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    qte_ok: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qte_nok: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qte_scrap: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qte_rework: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)
