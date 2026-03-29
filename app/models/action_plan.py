from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ActionPlan(Base):
    __tablename__ = "action_plans"
    __table_args__ = (
        CheckConstraint("realisation >= 0 AND realisation <= 100", name="ck_action_plans_realisation_range"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    numero: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    cv: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    zone: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    non_conformite: Mapped[str] = mapped_column(Text, nullable=False)
    cause: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    commentaires: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    realisation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    efficacite: Mapped[str] = mapped_column(String(30), nullable=False, default="En cours", index=True)
    responsable: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, onupdate=func.now())
