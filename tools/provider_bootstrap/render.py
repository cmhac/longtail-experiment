"""Scaffold template rendering for provider bootstrap."""

from __future__ import annotations

from pathlib import Path
from string import Template


def render_scaffold(template_path: Path, context: dict[str, str]) -> str:
    template = Template(template_path.read_text(encoding="utf-8"))
    return template.safe_substitute(context)
