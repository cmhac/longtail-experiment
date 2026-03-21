"""US3 geography hierarchy schema and non-geographic marker support."""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, Field, model_validator


class GeographyNode(BaseModel):
    """One geography node supporting hierarchical and non-geographic series."""

    ALLOWED_KINDS: ClassVar[set[str]] = {
        "region",
        "country",
        "state",
        "county",
        "city",
        "non_geographic",
    }

    geo_id: str = Field(min_length=1)
    parent_id: str | None = None
    kind: str = Field(min_length=1)

    @classmethod
    def non_geographic_marker(cls) -> GeographyNode:
        """Return the canonical marker node for non-geographic series."""
        return cls(geo_id="__non_geographic__", parent_id=None, kind="non_geographic")

    @model_validator(mode="after")
    def _validate_kind_and_parent(self) -> GeographyNode:
        if self.kind not in self.ALLOWED_KINDS:
            raise ValueError("invalid geography kind")
        if self.parent_id is not None and self.parent_id == self.geo_id:
            raise ValueError("geography cannot reference itself as parent")
        return self
