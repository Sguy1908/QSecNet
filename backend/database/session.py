"""Database engine and request-scoped SQLAlchemy session handling."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import get_settings


def _engine_kwargs(database_url: str) -> dict[str, object]:
    return {"connect_args": {"check_same_thread": False}} if database_url.startswith("sqlite") else {}


engine = create_engine(get_settings().database_url, future=True, **_engine_kwargs(get_settings().database_url))
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def get_session() -> Generator[Session, None, None]:
    """Yield a transaction session suitable for FastAPI dependency injection."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
<<<<<<< HEAD
=======


def initialize_database() -> None:
    """Create tables for the local deployment."""
    import backend.models.records  # noqa: F401
    import backend.models.topology  # noqa: F401

    Base.metadata.create_all(engine)
>>>>>>> origin/main
