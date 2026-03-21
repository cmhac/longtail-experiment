"""Tracing helpers for pipeline contract processing."""

from __future__ import annotations

from opentelemetry import trace


def get_contract_tracer(name: str = "pipeline.contract") -> trace.Tracer:
    """Return a tracer for contract ingestion components."""
    return trace.get_tracer(name)
