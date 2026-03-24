"""Structured CLI output helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BootstrapError(Exception):
    code: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


def emit_success(
    *, generated_file: str, source_key: str, next_steps: list[str]
) -> None:
    print("STATUS: success")
    print(f"GENERATED_FILE: {generated_file}")
    print(f"SOURCE_KEY: {source_key}")
    print("NEXT_STEPS:")
    for step in next_steps:
        print(f"- {step}")


def emit_failure(*, error_code: str, message: str) -> None:
    print("STATUS: failure")
    print(f"ERROR_CODE: {error_code}")
    print(f"MESSAGE: {message}")
