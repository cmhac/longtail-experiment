"""Source-asset migration helpers for orchestration runtime and triggers."""

from .authority_state import (
    AuthorityMode,
    SchedulingAuthorityState,
    assert_dagster_only_authority,
    dagster_only_authority_state,
)
from .contracts import (
    SourceAssetContractError,
    format_contract_error,
    register_source_assets,
    validate_registration,
)
from .discovery import (
    SourceBuilderSpec,
    discover_series_catalog_entries,
    discover_source_registrations,
)
from .outcomes import build_failure_summary
from .ownership_mode import (
    OwnershipMode,
    SeriesOwnershipModeRecord,
    build_ownership_mode_registry,
    validate_ownership_mode_windows,
)
from .ownership_transition import apply_ownership_transition
from .recovery import build_post_cutover_recovery_plan
from .series_catalog import SeriesCatalogEntry, validate_series_catalog_entries
from .series_selection import (
    SeriesSelectionResolution,
    normalize_requested_series_item_keys,
    resolve_series_selection,
)
from .triggering import (
    build_invalid_source_request_summary,
    normalize_requested_source_keys,
    validate_source_selection,
)

__all__ = [
    "AuthorityMode",
    "SchedulingAuthorityState",
    "SourceAssetContractError",
    "SourceBuilderSpec",
    "SeriesCatalogEntry",
    "SeriesOwnershipModeRecord",
    "OwnershipMode",
    "assert_dagster_only_authority",
    "build_ownership_mode_registry",
    "apply_ownership_transition",
    "build_failure_summary",
    "build_invalid_source_request_summary",
    "build_post_cutover_recovery_plan",
    "dagster_only_authority_state",
    "discover_series_catalog_entries",
    "discover_source_registrations",
    "format_contract_error",
    "normalize_requested_source_keys",
    "normalize_requested_series_item_keys",
    "register_source_assets",
    "resolve_series_selection",
    "SeriesSelectionResolution",
    "validate_ownership_mode_windows",
    "validate_registration",
    "validate_series_catalog_entries",
    "validate_source_selection",
]
