"""Dummy source provider workflow used for first end-to-end ingest runs."""

from __future__ import annotations

from dataclasses import dataclass

from ..source_ingest_runner import SourceIngestRunner
from ..source_schedule_policy import SourceSchedulePolicy
from ..workflow_registry import SourceWorkflowRegistration
from ..workflow_request import SourceWorkflowRequest

DUMMY_SOURCE_KEY = "dummy_source"


@dataclass(frozen=True)
class DummySourceProvider:
    """Provider that emits deterministic payloads for orchestration validation."""

    source_name: str = "Dummy Bureau"

    def fetch_records(self) -> list[dict[str, object]]:
        """Return a deterministic payload batch that passes canonical validation."""
        return [
            {
                "source_name": self.source_name,
                "source_type": "external",
                "series_key": "DUMMY.US.CPI",
                "metric_name": "Dummy CPI",
                "dataset_title": "Dummy CPI",
                "dataset_description": (
                    "Deterministic CPI sample series used for pipeline validation."
                ),
                "dataset_geographic_scope": "United States",
                "topic_tags": ["inflation", "prices", "demo"],
                "frequency": "monthly",
                "date": "2026-02-01",
                "reported_at": "2026-03-01T00:00:00Z",
                "value": "123.45",
            }
        ]


def build_dummy_source_workflow(
    runner: SourceIngestRunner,
    provider: DummySourceProvider | None = None,
    schedule_policy: SourceSchedulePolicy | None = None,
) -> SourceWorkflowRegistration:
    """Build a dummy source workflow registration for Dagster runtime validation."""
    source_provider = provider or DummySourceProvider()

    def _handler(request: SourceWorkflowRequest):
        records = request.run_context.get("records")
        if records is None:
            records = source_provider.fetch_records()
        if not isinstance(records, list):
            raise ValueError("run_context.records must be a list")
        return runner.run_records(request=request, records=records)

    return SourceWorkflowRegistration(
        workflow_id="wf-dummy-source",
        source_key=DUMMY_SOURCE_KEY,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
        schedule_policy=schedule_policy,
    )
