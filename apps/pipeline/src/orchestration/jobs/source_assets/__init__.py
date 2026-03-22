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
from .discovery import SourceBuilderSpec, discover_source_registrations
from .outcomes import build_failure_summary
from .recovery import build_post_cutover_recovery_plan
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
    "assert_dagster_only_authority",
    "build_failure_summary",
    "build_invalid_source_request_summary",
    "build_post_cutover_recovery_plan",
    "dagster_only_authority_state",
    "discover_source_registrations",
    "format_contract_error",
    "normalize_requested_source_keys",
    "register_source_assets",
    "validate_registration",
    "validate_source_selection",
]
