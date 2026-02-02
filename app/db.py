import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def _normalize_db_url(url: str | None) -> str:
    if not url:
        raise RuntimeError("DATABASE_URL is not set in environment variables.")

    # Render sometimes provides postgres:// which SQLAlchemy prefers as postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    return url

DATABASE_URL = _normalize_db_url(os.getenv("DATABASE_URL"))

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
