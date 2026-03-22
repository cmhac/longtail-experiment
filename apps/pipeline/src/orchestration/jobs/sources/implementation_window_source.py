"""Implementation-window source fixture used during source-asset migration."""

from __future__ import annotations

from dataclasses import dataclass

from ..source_ingest_runner import SourceIngestRunner
from ..source_schedule_policy import SourceSchedulePolicy
from ..workflow_registry import SourceWorkflowRegistration
from ..workflow_request import SourceWorkflowRequest

IMPLEMENTATION_WINDOW_SOURCE_KEY = "implementation_window_source"


@dataclass(frozen=True)
class ImplementationWindowSourceProvider:
    """Provider emitting deterministic data for migration-window validation."""

    source_name: str = "Implementation Window Source"

    def fetch_records(self) -> list[dict[str, object]]:
        """Return deterministic records used to validate onboarding in-flight."""
        return [
            {
                "source_name": self.source_name,
                "source_type": "external",
                "series_key": "IMPL.US.WINDOW",
                "metric_name": "Implementation Window Metric",
                "frequency": "daily",
                "date": "2026-03-22",
                "reported_at": "2026-03-22T00:00:00Z",
                "value": "42.0",
            }
        ]


def build_implementation_window_source_workflow(
    runner: SourceIngestRunner,
    provider: ImplementationWindowSourceProvider | None = None,
    schedule_policy: SourceSchedulePolicy | None = None,
) -> SourceWorkflowRegistration:
    """Build source workflow registration for implementation-window fixtures."""
    source_provider = provider or ImplementationWindowSourceProvider()

    def _handler(request: SourceWorkflowRequest):
        records = request.run_context.get("records")
        if records is None:
            records = source_provider.fetch_records()
        if not isinstance(records, list):
            raise ValueError("run_context.records must be a list")
        return runner.run_records(request=request, records=records)

    return SourceWorkflowRegistration(
        workflow_id="wf-implementation-window-source",
        source_key=IMPLEMENTATION_WINDOW_SOURCE_KEY,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
        schedule_policy=schedule_policy,
    )
