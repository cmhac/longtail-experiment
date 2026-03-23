"""Source-group projection helpers for catalog responses."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def project_catalog_source_groups(
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Group catalog items by source name/id and return deterministic groups."""
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        source_payload = item.get("source")
        source = source_payload if isinstance(source_payload, dict) else {}
        source_id = str(source.get("id", ""))
        source_name = str(source.get("name", ""))
        grouped[(source_name, source_id)].append(item)

    groups: list[dict[str, Any]] = []
    for (source_name, source_id), source_items in sorted(grouped.items()):
        groups.append(
            {
                "source": {"id": source_id, "name": source_name},
                "dataset_count": len(source_items),
                "dataset_ids": [str(item.get("dataset_id", "")) for item in source_items],
            }
        )
    return groups
