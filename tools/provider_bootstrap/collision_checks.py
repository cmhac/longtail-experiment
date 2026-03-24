"""Collision checks for bootstrap generation."""

from __future__ import annotations

import ast
from pathlib import Path


def ensure_output_path_available(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"output adapter already exists: {path}")


def existing_source_keys(source_dir: Path) -> set[str]:
    keys: set[str] = set()
    if not source_dir.exists():
        return keys

    for file_path in sorted(source_dir.glob("*_source.py")):
        keys.update(_extract_source_keys(file_path))
    return keys


def ensure_source_key_available(source_key: str, *, source_dir: Path) -> None:
    keys = existing_source_keys(source_dir)
    if source_key in keys:
        raise ValueError(f"source_key collision detected: {source_key}")


def _extract_source_keys(file_path: Path) -> set[str]:
    """Extract literal source_key values from SOURCE_SPEC dict assignments."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
    except SyntaxError:
        return set()

    keys: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        target_names = {t.id for t in node.targets if isinstance(t, ast.Name)}
        if "SOURCE_SPEC" not in target_names:
            continue
        if not isinstance(node.value, ast.Dict):
            continue

        for key_node, value_node in zip(node.value.keys, node.value.values, strict=False):
            if not isinstance(key_node, ast.Constant) or key_node.value != "source_key":
                continue
            if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
                keys.add(value_node.value)

    return keys
