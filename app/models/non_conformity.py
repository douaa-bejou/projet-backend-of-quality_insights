from datetime import date, datetime

from sqlalchemy import BigInteger, CheckConstraint, Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NonConformity(Base):
    __tablename__ = "non_conformities"
    __table_args__ = (
        CheckConstraint("qte_nok >= 0", name="ck_non_conformities_qte_nok_non_negative"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    numero: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, unique=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    semaine: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    mois: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    designation: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    defaut: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    qte_nok: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    zone: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    poste: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    responsable: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="Ouverte", index=True)
    priorite: Mapped[str] = mapped_column(String(20), nullable=False, default="Moyenne", index=True)
    date_echeance: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    commentaires: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_plan_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), index=True)
