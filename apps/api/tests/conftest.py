from collections.abc import Generator

import pytest
from app.db.session import Base
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def db_engine():
    """Create an isolated in-memory engine for persistence tests."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def db_session(db_engine) -> Generator[Session, None, None]:
    """Yield a transaction-scoped SQLAlchemy session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionTesting = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = SessionTesting()

    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()
