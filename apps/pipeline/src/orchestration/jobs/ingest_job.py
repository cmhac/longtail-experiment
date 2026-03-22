"""Dagster job definition for orchestration ingest entrypoint."""

from __future__ import annotations

from dagster import job, op


@op
def emit_ingest_placeholder() -> str:
    """Emit a placeholder value while source-specific wiring evolves."""
    return "ingest-ready"


@job
def ingest_job() -> None:
    """Top-level Dagster job used by schedule and sensor triggers."""
    emit_ingest_placeholder()
