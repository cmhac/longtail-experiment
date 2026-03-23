"""US2 tests for migration revision status verification behavior."""

from __future__ import annotations

from pathlib import Path


def test_revision_check_uses_expected_baseline_default() -> None:
    script = Path("tools/quality/local-stack/check-db-revision.sh").read_text(
        encoding="utf-8"
    )
    assert (
        'EXPECTED_REVISION="${EXPECTED_DB_REVISION:-0007_dataset_metadata_topic_tags}"'
        in script
    )


def test_revision_check_exits_on_mismatch() -> None:
    script = Path("tools/quality/local-stack/check-db-revision.sh").read_text(
        encoding="utf-8"
    )
    assert "Revision mismatch" in script
    assert "exit 1" in script
    assert "Revision OK" in script
