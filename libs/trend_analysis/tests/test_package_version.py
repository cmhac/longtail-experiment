"""Smoke tests for trend-analysis package scaffold."""

from trend_analysis import LIBRARY_VERSION


def test_library_version_exposed() -> None:
    """Library version should be publicly importable for analysis identity coupling."""
    assert LIBRARY_VERSION == "0.1.0"
