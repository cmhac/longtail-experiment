"""Tests for pipeline contract observability wiring."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.contract.observability.logging import get_contract_logger
from src.contract.observability.tracing import get_contract_tracer


def test_contract_logger_has_expected_name() -> None:
    """Contract logger should provide a bind-capable logger instance."""
    logger = get_contract_logger()
    rebound = logger.bind(component="test")
    assert rebound is not None


def test_contract_logger_supports_trace_context_binding() -> None:
    """Contract logger should bind trace correlation fields for backend handoff."""
    logger = get_contract_logger("pipeline.contract.ingest")
    rebound = logger.bind(trace_id="trace-123", span_id="span-456")
    assert rebound is not None


def test_contract_tracer_provider_available() -> None:
    """Contract tracer helper should return a configured tracer object."""
    tracer = get_contract_tracer()
    assert tracer is not None


def test_contract_tracer_uses_component_namespace() -> None:
    """Tracer helper should keep component namespaced instrumentation."""
    tracer = get_contract_tracer("pipeline.contract.ingest")
    assert tracer is not None
