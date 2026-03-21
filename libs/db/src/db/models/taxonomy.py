"""Taxonomy hierarchy models for category and geography."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CategoryNode(Base):
    """Category hierarchy node."""

    __tablename__ = "category_nodes"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("category_nodes.id"), nullable=True
    )

    parent: Mapped["CategoryNode | None"] = relationship(
        remote_side=[id], back_populates="children"
    )
    children: Mapped[list["CategoryNode"]] = relationship(back_populates="parent")


class GeographyNode(Base):
    """Geography hierarchy node with explicit non-geographic marker."""

    __tablename__ = "geography_nodes"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_global: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    parent_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("geography_nodes.id"), nullable=True
    )

    parent: Mapped["GeographyNode | None"] = relationship(
        remote_side=[id], back_populates="children"
    )
    children: Mapped[list["GeographyNode"]] = relationship(back_populates="parent")
