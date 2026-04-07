"""US2 contract test for v2 as-of trend response payload."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.query.trend_descriptor_v2 import ObservationAsOfTrendV2Response
from tests.fixtures.trend_v2_payloads import canonical_available_v2, lookback_evidence_v2


def test_asof_v2_contract_model_accepts_evidence_payload() -> None:
    payload = ObservationAsOfTrendV2Response.model_validate(
        {
            "dataset_id": "UNRATE",
            "as_of_observed_on": "2026-03-01",
            "canonical_trend_descriptor": canonical_available_v2(),
            "lookback_trend_evidence": lookback_evidence_v2(),
        }
    )

    assert payload.dataset_id == "UNRATE"
    assert len(payload.lookback_trend_evidence) == 2
