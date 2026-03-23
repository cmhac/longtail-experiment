"""DB session dependency injection for FastAPI endpoints."""

from __future__ import annotations

import sys
from collections.abc import Generator
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parents[3] / "libs/db/src"
if str(_DB_PATH) not in sys.path:
    sys.path.insert(0, str(_DB_PATH))

from db import create_db_engine, create_session_factory, resolve_database_url  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402


def get_db_session() -> Generator[Session, None, None]:
    """Yield a per-request SQLAlchemy session and close it after the request."""
    url = resolve_database_url(explicit_url=None)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()
