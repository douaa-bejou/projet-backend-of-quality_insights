from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings

database_url = settings.database_url.strip()
if database_url.startswith("postgres://"):
    # Render/Heroku style URL compatibility for SQLAlchemy.
    database_url = database_url.replace("postgres://", "postgresql://", 1)

is_sqlite = database_url.startswith("sqlite")
is_sqlite_memory = database_url in {"sqlite://", "sqlite:///:memory:", "sqlite+pysqlite:///:memory:"}
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine_kwargs: dict = {"connect_args": connect_args} if connect_args else {}

if is_sqlite_memory:
    # Keep one shared in-memory DB connection for the app process.
    engine_kwargs["poolclass"] = StaticPool

engine = create_engine(database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
