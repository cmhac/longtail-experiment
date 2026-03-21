"""SC-005 ambiguity-rate verification tests for source onboarding."""

from __future__ import annotations

import json
from pathlib import Path

_SAMPLE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "sc005_ambiguity_samples.json"
_AMBIGUITY_RATE_TARGET = 0.1


def test_sc005_ambiguity_rate_stays_below_target() -> None:
    """Ambiguous source classifications should remain below 10%."""
    payload = json.loads(_SAMPLE_PATH.read_text(encoding="utf-8"))
    ambiguous = sum(1 for sample in payload["samples"] if sample["ambiguous"] is True)
    rate = ambiguous / len(payload["samples"])

    assert rate <= _AMBIGUITY_RATE_TARGET
