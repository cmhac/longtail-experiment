"""DB engine construction helpers."""

from sqlalchemy import Engine, create_engine


def create_db_engine(database_url: str, *, echo: bool = False) -> Engine:
    """Build a SQLAlchemy engine for the shared DB package."""
    return create_engine(database_url, echo=echo, pool_pre_ping=True)
