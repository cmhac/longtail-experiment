"""US3 category hierarchy schema and integrity rules."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class CategoryNode(BaseModel):
    """One category node in a parent/child taxonomy tree."""

    category_id: str = Field(min_length=1)
    parent_id: str | None = None
    label: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_self_parent(self) -> CategoryNode:
        if self.parent_id is not None and self.parent_id == self.category_id:
            raise ValueError("category cannot reference itself as parent")
        return self
