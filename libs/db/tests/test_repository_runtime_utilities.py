"""Unit tests for shared db repository utility modules."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, cast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from db.engine import create_db_engine
from db.repositories.hierarchy_repository import InMemoryHierarchyRepository
from db.repositories.observation_repository import InMemoryObservationRepository
from db.repositories.provenance_repository import InMemoryProvenanceRepository
from db.session import create_session_factory, session_scope
from db.settings import build_local_database_url, resolve_database_url


class _Observation:
    def __init__(self) -> None:
        self.series_key = "INT.US.FEDFUNDS"
        self.metric_name = "Effective Federal Funds Rate"
        self.frequency_granularity = "daily"
        self.source_type = "external"
        self.observed_on = date(2026, 1, 3)
        self.reported_at = "2026-01-04T00:00:00Z"
        self.value = Decimal("4.33")
        self.attributes = {"provider_series_id": "FEDFUNDS"}


class _FakeSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


class _FakeSessionFactory:
    def __init__(self) -> None:
        self.session = _FakeSession()

    def __call__(self) -> _FakeSession:
        return self.session


def test_hierarchy_repository_registers_and_reads_descendants() -> None:
    repo = InMemoryHierarchyRepository()

    repo.register_descendants("us", ["us-ca", "us-ny"])

    assert repo.get_descendant_ids("us") == ["us-ca", "us-ny"]
    assert repo.get_descendant_ids("missing") == []


def test_observation_repository_upserts_and_sorts_rows() -> None:
    repo = InMemoryObservationRepository()

    repo.upsert_value("INT.US.FEDFUNDS", date(2026, 1, 2), Decimal("4.25"))
    repo.upsert_observation(_Observation())

    rows = repo.list_observations()

    assert len(rows) == 2
    assert rows[0]["observed_on"] == date(2026, 1, 2)
    assert rows[1]["metric_name"] == "Effective Federal Funds Rate"


def test_provenance_repository_is_immutable_per_observation() -> None:
    repo = InMemoryProvenanceRepository()

    repo.add_release("obs-1", "rel-1", "https://example.com")

    stored = repo.get_release("obs-1")
    assert stored is not None
    assert stored.release_id == "rel-1"

    try:
        repo.add_release("obs-1", "rel-2", "https://example.com/new")
        raised = False
    except ValueError:
        raised = True
    assert raised is True


def test_settings_helpers_build_and_resolve_database_url() -> None:
    url_default = build_local_database_url(environment={})
    url_custom = build_local_database_url(
        environment={
            "LOCAL_DB_USER": "user",
            "LOCAL_DB_PASSWORD": "pass",
            "LOCAL_DB_HOST": "host",
            "LOCAL_DB_PORT": "6543",
            "LOCAL_DB_NAME": "db_name",
        }
    )

    assert (
        url_default
        == "postgresql+psycopg://longtail:longtail@127.0.0.1:55432/longtail_local"
    )
    assert url_custom == "postgresql+psycopg://user:pass@host:6543/db_name"

    assert (
        resolve_database_url(explicit_url="postgresql://explicit", environment={})
        == "postgresql://explicit"
    )
    assert (
        resolve_database_url(
            explicit_url="postgresql://ignored",
            environment={"DATABASE_URL": "postgresql://override"},
        )
        == "postgresql://override"
    )


def test_engine_and_session_scope_helpers_cover_commit_and_rollback_paths() -> None:
    engine = create_db_engine("sqlite+pysqlite:///:memory:")
    session_factory = create_session_factory(engine)
    assert session_factory.kw["bind"] is engine

    fake_factory = _FakeSessionFactory()
    with session_scope(cast(Any, fake_factory)):
        pass
    assert fake_factory.session.committed is True
    assert fake_factory.session.closed is True

    fake_factory_error = _FakeSessionFactory()
    try:
        with session_scope(cast(Any, fake_factory_error)):
            raise RuntimeError("boom")
    except RuntimeError:
        pass

    assert fake_factory_error.session.rolled_back is True
    assert fake_factory_error.session.closed is True
