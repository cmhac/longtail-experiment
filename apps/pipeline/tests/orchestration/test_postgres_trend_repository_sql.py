"""SQL rendering regressions for Postgres trend repository writes."""

from pathlib import Path


def test_trend_repository_uses_cast_for_optional_observation_id() -> None:
    """Named SQL params should cast observation_id without psycopg colon syntax errors."""
    source = Path(
        "apps/pipeline/src/orchestration/resources/postgres_trend_repository.py"
    ).read_text(encoding="utf-8")

    assert "CAST(:observation_id AS UUID)" in source
    assert ":observation_id::uuid" not in source
