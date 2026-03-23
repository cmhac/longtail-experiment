"""Contract tests for error branches in dataset discovery service and validators."""

# ruff: noqa: D103, PLR2004

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.errors import ContractQueryError
from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.dataset_discovery_validators import (
    normalize_page,
    normalize_page_size,
    normalize_query_text,
    normalize_recent_limit,
    parse_optional_date,
)


class _BrokenRepository:
    pass


class _InvalidPayloadRepository:
    def search_datasets(self, **_: object) -> tuple[str, str]:
        return "bad", "bad"

    def list_recent_datasets(self, **_: object) -> str:
        return "bad"

    def list_catalog_datasets(self, **_: object) -> tuple[str, str]:
        return "bad", "bad"

    def get_dataset_detail(self, **_: object) -> str:
        return "bad"

    def list_dataset_observations(self, **_: object) -> str:
        return "bad"


def test_service_raises_when_repository_contract_methods_missing() -> None:
    service = DatasetDiscoveryService(_BrokenRepository())

    with pytest.raises(ContractQueryError):
        service.search_datasets(query_text=None, page=1, page_size=10)

    with pytest.raises(ContractQueryError):
        service.list_recent_updates(limit=5)

    with pytest.raises(ContractQueryError):
        service.list_catalog(
            query_text=None,
            source_id=None,
            page=1,
            page_size=20,
            group_by_source=False,
        )

    with pytest.raises(ContractQueryError):
        service.get_dataset_detail(dataset_id="UNRATE", from_date=None, to_date=None)


def test_service_raises_when_repository_returns_invalid_payload_shape() -> None:
    service = DatasetDiscoveryService(_InvalidPayloadRepository())

    with pytest.raises(ContractQueryError):
        service.search_datasets(query_text=None, page=1, page_size=10)

    with pytest.raises(ContractQueryError):
        service.list_recent_updates(limit=5)

    with pytest.raises(ContractQueryError):
        service.list_catalog(
            query_text=None,
            source_id=None,
            page=1,
            page_size=20,
            group_by_source=False,
        )

    with pytest.raises(ContractQueryError):
        service.get_dataset_detail(dataset_id="UNRATE", from_date=None, to_date=None)


def test_validator_success_and_error_paths_cover_defaults() -> None:
    assert normalize_page(None) == 1
    assert normalize_page_size(None) == 20
    assert normalize_recent_limit(None) == 5
    assert normalize_query_text("   ") is None
    assert normalize_query_text(" labor ") == "labor"
    assert parse_optional_date(None, field_name="from_date") is None

    with pytest.raises(ContractQueryError):
        parse_optional_date("invalid-date", field_name="from_date")
