"""Seed data used by the local backend HTTP API discovery server."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

_DATASETS: list[dict[str, Any]] = [
    {
        "dataset_id": "FEDFUNDS",
        "source": {"id": "fred", "name": "FRED"},
        "title": "Federal Funds Effective Rate",
        "description": "Interest rate at which depository institutions lend balances overnight.",
        "geographic_scope": "US",
        "topic_tags": ["interest rates", "monetary policy"],
        "metadata": {"units": "Percent"},
    },
    {
        "dataset_id": "UNRATE",
        "source": {"id": "fred", "name": "FRED"},
        "title": "Unemployment Rate",
        "description": "Percent of labor force unemployed",
        "geographic_scope": "US",
        "topic_tags": ["labor", "employment"],
        "metadata": {"units": "Percent"},
    },
    {
        "dataset_id": "GDP",
        "source": {"id": "bea", "name": "BEA"},
        "title": "Gross Domestic Product",
        "description": "Quarterly real GDP",
        "geographic_scope": "US",
        "topic_tags": ["growth"],
        "metadata": {"units": "Billions of Chained 2017 Dollars"},
    },
]

_OBSERVATIONS: list[dict[str, Any]] = [
    {
        "dataset_id": "FEDFUNDS",
        "observed_on": "2025-12-01",
        "value": 4.33,
        "reported_at": "2026-01-02T00:00:00Z",
        "attributes": {"revision": 0},
    },
    {
        "dataset_id": "FEDFUNDS",
        "observed_on": "2026-01-01",
        "value": 4.33,
        "reported_at": "2026-02-03T00:00:00Z",
        "attributes": {"revision": 0},
    },
    {
        "dataset_id": "UNRATE",
        "observed_on": "2026-01-01",
        "value": 4.0,
        "reported_at": "2026-01-10T00:00:00Z",
        "attributes": {"revision": 0},
    },
    {
        "dataset_id": "GDP",
        "observed_on": "2025-10-01",
        "value": 23499.0,
        "reported_at": "2026-01-30T00:00:00Z",
        "attributes": {"revision": 1},
    },
]


def load_discovery_seed_data() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return deep-copied seed rows for datasets and observations."""
    return deepcopy(_DATASETS), deepcopy(_OBSERVATIONS)
