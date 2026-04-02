from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings


is_sqlite = settings.database_url.startswith("sqlite")
is_sqlite_memory = settings.database_url in {"sqlite://", "sqlite:///:memory:", "sqlite+pysqlite:///:memory:"}
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine_kwargs: dict = {"connect_args": connect_args} if connect_args else {}

if is_sqlite_memory:
    # Keep one shared in-memory DB connection for the app process.
    engine_kwargs["poolclass"] = StaticPool

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
