"""Unit tests for provider bootstrap rendering."""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
MODULE_PATH = REPO_ROOT / "tools/provider_bootstrap/render.py"
MODULE_SPEC = importlib.util.spec_from_file_location("provider_bootstrap_render", MODULE_PATH)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
render_module = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(render_module)

render_scaffold = render_module.render_scaffold


def test_render_scaffold_substitutes_context(tmp_path: Path) -> None:
    """Template renderer should replace placeholders with provided values."""
    template = tmp_path / "template.txt"
    template.write_text("hello ${name}", encoding="utf-8")

    rendered = render_scaffold(template, {"name": "world"})

    assert rendered == "hello world"
