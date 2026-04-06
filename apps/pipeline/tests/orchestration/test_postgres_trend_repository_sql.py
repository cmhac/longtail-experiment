"""SQL rendering regressions for Postgres trend repository writes."""

from pathlib import Path


def test_trend_repository_uses_cast_for_optional_observation_id() -> None:
    """Named SQL params should cast observation_id without psycopg colon syntax errors."""
    source = Path(
        "apps/pipeline/src/orchestration/resources/postgres_trend_repository.py"
    ).read_text(encoding="utf-8")

    assert "CAST(:observation_id AS UUID)" in source
    assert ":observation_id::uuid" not in source


def test_trend_repository_includes_notification_sql_paths() -> None:
    """Notification SQL statements should exist in Postgres trend repository."""

    source = Path(
        "apps/pipeline/src/orchestration/resources/postgres_trend_repository.py"
    ).read_text(encoding="utf-8")

    assert "INSERT INTO trend_change_events" in source
    assert "ON CONFLICT (idempotency_fingerprint) DO NOTHING" in source
    assert "INSERT INTO user_trend_notifications" in source
    assert "ON CONFLICT (event_id, user_id) DO NOTHING" in source
    assert "ua.account_status = 'active'" in source
