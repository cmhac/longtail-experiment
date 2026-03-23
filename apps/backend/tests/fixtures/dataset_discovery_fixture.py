"""Shared sample fixture records for dataset discovery contract tests."""

from __future__ import annotations

from copy import deepcopy

_DISCOVERY_FIXTURE: dict[str, object] = {
    "datasets": [
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
            "dataset_id": "CPIAUCSL",
            "source": {"id": "fred", "name": "FRED"},
            "title": "Consumer Price Index",
            "description": "All Urban Consumers",
            "geographic_scope": "US",
            "topic_tags": ["inflation", "prices"],
            "metadata": {"units": "Index"},
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
    ],
    "observations": [
        {
            "dataset_id": "UNRATE",
            "observed_on": "2026-01-01",
            "value": 4.0,
            "reported_at": "2026-01-10T00:00:00Z",
            "attributes": {"revision": 0},
        },
        {
            "dataset_id": "UNRATE",
            "observed_on": "2026-02-01",
            "value": 4.1,
            "reported_at": "2026-02-10T00:00:00Z",
            "attributes": {"revision": 0},
        },
        {
            "dataset_id": "CPIAUCSL",
            "observed_on": "2026-01-01",
            "value": 309.2,
            "reported_at": "2026-02-15T00:00:00Z",
            "attributes": {"revision": 0},
        },
        {
            "dataset_id": "GDP",
            "observed_on": "2025-10-01",
            "value": 23499.0,
            "reported_at": "2026-01-30T00:00:00Z",
            "attributes": {"revision": 1},
        },
    ],
}


def dataset_discovery_fixture() -> dict[str, object]:
    """Return a deep-copied fixture dictionary for isolated test mutation."""
    return deepcopy(_DISCOVERY_FIXTURE)
