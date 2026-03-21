"""SC-001 onboarding-rate verification tests."""

from __future__ import annotations

import json
from pathlib import Path

_SAMPLE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "sc001_onboarding_samples.json"
_ONBOARDING_TARGET = 0.9


def test_sc001_onboarding_success_rate_meets_target() -> None:
    """At least 90% of onboarding samples should pass contract validation."""
    payload = json.loads(_SAMPLE_PATH.read_text(encoding="utf-8"))
    successful = sum(1 for sample in payload["samples"] if sample["onboarded"] is True)
    rate = successful / len(payload["samples"])

    assert rate >= _ONBOARDING_TARGET
