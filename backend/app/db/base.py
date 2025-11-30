from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# For now, use a synchronous engine; that’s perfectly fine with FastAPI.
engine = create_engine(
    settings.database_url,
    echo=False,        # set True if you want to see SQL in logs
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# FastAPI dependency to get a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
