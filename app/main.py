from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api import api_router
from app.config import settings
from app.database import Base, engine
from app.database_migrations import apply_runtime_migrations
from app import models  # noqa: F401
from app.models import User
from app.services import hash_password


def ensure_bootstrap_admin() -> None:
    email = settings.bootstrap_admin_email.strip().lower()
    password = settings.bootstrap_admin_password
    name = settings.bootstrap_admin_name.strip() or "Responsable"

    if not email or not password:
        return

    with Session(engine) as db:
        existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if existing:
            existing.name = name
            existing.password_hash = hash_password(password)
            db.add(existing)
            db.commit()
            return

        user = User(name=name, email=email, password_hash=hash_password(password))
        db.add(user)
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    apply_runtime_migrations(engine)
    ensure_bootstrap_admin()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
