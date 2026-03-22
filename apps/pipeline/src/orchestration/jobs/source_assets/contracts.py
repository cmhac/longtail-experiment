"""Contract validation helpers for source-asset registration."""

from __future__ import annotations

from dataclasses import dataclass

from ..workflow_registry import SourceWorkflowRegistration, SourceWorkflowRegistry


@dataclass(frozen=True)
class SourceAssetContractError(ValueError):
    """Raised when source registration fails contract validation."""

    module_name: str
    source_key: str
    reason: str

    def __str__(self) -> str:
        return format_contract_error(self)


def format_contract_error(error: SourceAssetContractError) -> str:
    """Format a stable, actionable source registration contract error."""
    return (
        "source asset contract violation: "
        f"module={error.module_name} source_key={error.source_key} reason={error.reason}"
    )


def validate_registration(
    registration: SourceWorkflowRegistration,
    *,
    module_name: str,
) -> None:
    """Validate one source registration against the contract."""
    if registration.status != "active":
        raise SourceAssetContractError(
            module_name=module_name,
            source_key=registration.source_key,
            reason="registration must be active",
        )
    if not registration.source_key.strip():
        raise SourceAssetContractError(
            module_name=module_name,
            source_key=registration.source_key,
            reason="source_key must be non-empty",
        )
    if not registration.workflow_id.strip():
        raise SourceAssetContractError(
            module_name=module_name,
            source_key=registration.source_key,
            reason="workflow_id must be non-empty",
        )


def register_source_assets(
    *,
    registry: SourceWorkflowRegistry,
    registrations: list[tuple[str, SourceWorkflowRegistration]],
) -> None:
    """Validate and register discovered source assets."""
    seen_source_keys: dict[str, str] = {}
    for module_name, registration in registrations:
        validate_registration(registration, module_name=module_name)
        existing = seen_source_keys.get(registration.source_key)
        if existing is not None:
            raise SourceAssetContractError(
                module_name=module_name,
                source_key=registration.source_key,
                reason=f"duplicate source_key also declared by {existing}",
            )
        seen_source_keys[registration.source_key] = module_name

    for _, registration in registrations:
        registry.register(registration)
