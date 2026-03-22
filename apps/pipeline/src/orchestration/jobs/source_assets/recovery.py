"""Post-cutover recovery helpers for failed source runs."""

from __future__ import annotations

from .authority_state import SchedulingAuthorityState, assert_dagster_only_authority


def build_post_cutover_recovery_plan(
    *,
    authority_state: SchedulingAuthorityState,
    source_results: list[dict[str, object]],
) -> dict[str, object]:
    """Build source-level recovery plan without re-enabling legacy scheduling."""
    assert_dagster_only_authority(authority_state)

    failed_sources = sorted(
        {
            str(result["source_key"])
            for result in source_results
            if str(result.get("status")) == "failure"
        }
    )

    return {
        "authority_mode": authority_state.authority_mode,
        "legacy_paths_disabled": authority_state.legacy_paths_disabled,
        "failed_sources": failed_sources,
        "requires_manual_recovery": len(failed_sources) > 0,
    }
