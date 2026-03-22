"""Reference source adapter used by onboarding tests and docs."""

from __future__ import annotations

from ..source_ingest_runner import SourceIngestRunner
from ..workflow_registry import SourceWorkflowRegistration
from ..workflow_request import SourceWorkflowRequest

EXAMPLE_SOURCE_KEY = "example_source"


def build_example_source_workflow(runner: SourceIngestRunner) -> SourceWorkflowRegistration:
    """Build a workflow registration backed by the reusable source ingest runner."""

    def _handler(request: SourceWorkflowRequest):
        records = request.run_context.get("records", [])
        if not isinstance(records, list):
            raise ValueError("run_context.records must be a list")
        return runner.run_records(request=request, records=records)

    return SourceWorkflowRegistration(
        workflow_id="wf-example-source",
        source_key=EXAMPLE_SOURCE_KEY,
        owner="pipeline",
        supported_trigger_modes={"scheduled", "on_demand"},
        handler=_handler,
    )
