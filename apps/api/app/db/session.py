from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Base declarative class for all persistence models."""


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Session:
    """Yield a SQLAlchemy session for request-scoped dependencies."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
