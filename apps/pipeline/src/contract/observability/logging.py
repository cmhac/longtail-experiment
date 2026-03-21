"""Structured logging setup for pipeline contract processing."""

from __future__ import annotations

import structlog


def get_contract_logger(name: str = "pipeline.contract") -> structlog.stdlib.BoundLogger:
    """Return a logger for contract ingestion components."""
    return structlog.get_logger(name)
