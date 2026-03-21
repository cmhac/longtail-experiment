"""Declarative base for shared contract database models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all shared database ORM models."""
