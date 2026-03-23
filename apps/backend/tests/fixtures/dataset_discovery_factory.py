"""Factory helpers that produce test fixtures for dataset discovery tests."""

from __future__ import annotations

from typing import Any, cast

from .dataset_discovery_fixture import dataset_discovery_fixture


def build_discovery_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return datasets and observations rows as independent mutable lists."""
    fixture = dataset_discovery_fixture()
    datasets = cast(list[dict[str, Any]], fixture["datasets"])
    observations = cast(list[dict[str, Any]], fixture["observations"])
    return datasets, observations
