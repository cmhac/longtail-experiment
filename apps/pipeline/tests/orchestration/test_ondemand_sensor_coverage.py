"""Coverage tests for ondemand sensor logic via wrapped evaluation function."""

from __future__ import annotations

import sys
from pathlib import Path

from dagster import RunRequest, SkipReason
from dagster._core.definitions.sensor_definition import SensorEvaluationContext

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.orchestration.sensors.ondemand_sensor import ondemand_sensor


def test_ondemand_sensor_skip_path_with_blank_cursor() -> None:
    """Blank cursor should produce a skip reason."""
    context = SensorEvaluationContext(
        instance_ref=None,
        cursor="   ",
        last_run_key=None,
        repository_name=None,
        repository_def=None,
        sensor_name="ondemand_sensor",
        resources=None,
    )

    result = ondemand_sensor(context)

    assert isinstance(result, SkipReason)


def test_ondemand_sensor_run_request_path_with_token_cursor() -> None:
    """Token cursor should produce on-demand run request and clear cursor."""
    context = SensorEvaluationContext(
        instance_ref=None,
        cursor="queued-token-1",
        last_run_key=None,
        repository_name=None,
        repository_def=None,
        sensor_name="ondemand_sensor",
        resources=None,
    )

    result = ondemand_sensor(context)

    assert isinstance(result, RunRequest)
    assert result.run_key == "queued-token-1"
    assert result.tags == {
        "trigger_type": "on_demand",
        "requested_by": "ondemand_sensor",
        "source_selection_mode": "operator_requested",
    }
