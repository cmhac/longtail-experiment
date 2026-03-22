"""
Shared scheduled Dagster trigger — RETIRED after Feature 011 cutover.

This module previously defined an hourly all-source schedule. Per-source asset
schedules now own cadence authority. See source_asset_schedules.py.
"""

from __future__ import annotations

SHARED_SCHEDULE_RETIRED = True
"""Marker indicating the shared ingest schedule is no longer active."""
