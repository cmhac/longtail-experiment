"""Registry for source workflow registration and execution."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from .workflow_request import SourceWorkflowRequest
from .workflow_result import SourceWorkflowResult

if TYPE_CHECKING:
    from .source_schedule_policy import SourceSchedulePolicy


@dataclass(frozen=True)
class SourceWorkflowRegistration:
    """Registration metadata and handler for one source workflow."""

    workflow_id: str
    source_key: str
    owner: str
    supported_trigger_modes: set[str]
    handler: Callable[[SourceWorkflowRequest], SourceWorkflowResult]
    schedule_policy: SourceSchedulePolicy | None = None
    status: str = "active"


class SourceWorkflowRegistry:
    """Map active source keys to workflow handlers."""

    def __init__(self) -> None:
        """Initialize empty in-memory workflow registrations."""
        self._registrations: dict[str, SourceWorkflowRegistration] = {}

    def register(self, registration: SourceWorkflowRegistration) -> None:
        """Register one active workflow by source key."""
        if registration.status != "active":
            raise ValueError("only active workflows can be registered")
        if registration.source_key in self._registrations:
            raise ValueError(f"source workflow already registered: {registration.source_key}")
        self._registrations[registration.source_key] = registration

    def execute(self, request: SourceWorkflowRequest) -> SourceWorkflowResult:
        """Execute a workflow for the request source key."""
        registration = self._registrations.get(request.source_key)
        if registration is None:
            raise KeyError(f"unknown source workflow: {request.source_key}")
        if request.trigger_type not in registration.supported_trigger_modes:
            raise ValueError("trigger type is not supported by registered workflow")
        return registration.handler(request)

    def execute_for_source(
        self,
        *,
        source_key: str,
        run_id: str,
        trigger_type: Literal["scheduled", "on_demand"],
        run_context: dict[str, object],
    ) -> SourceWorkflowResult:
        """Execute one source with inline request values."""
        request = SourceWorkflowRequest(
            run_id=run_id,
            source_key=source_key,
            trigger_type=trigger_type,
            run_context=run_context,
        )
        return self.execute(request)

    def list_source_keys(self) -> list[str]:
        """Return all registered source keys in deterministic order."""
        return sorted(self._registrations.keys())

    def list_registrations(self) -> list[SourceWorkflowRegistration]:
        """Return registrations in deterministic source-key order."""
        return [
            self._registrations[source_key] for source_key in sorted(self._registrations.keys())
        ]
