"""Base repository helpers shared across all read repositories."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

_MAX_PAGE_SIZE = 200


def apply_pagination(
    session: Session,
    query: Any,
    *,
    page: int,
    page_size: int,
) -> tuple[list[Any], int]:
    """
    Apply page-number pagination to a SQLAlchemy select statement.

    Returns a (items, total) tuple where total is the count before pagination.
    page must be >= 1, page_size must be between 1 and 200 inclusive.
    """
    if page < 1:
        msg = "page must be >= 1"
        raise ValueError(msg)
    if page_size < 1 or page_size > _MAX_PAGE_SIZE:
        msg = f"page_size must be between 1 and {_MAX_PAGE_SIZE}"
        raise ValueError(msg)

    count_query = select(func.count()).select_from(query.subquery())
    total: int = session.scalar(count_query) or 0

    offset = (page - 1) * page_size
    paginated = session.scalars(query.offset(offset).limit(page_size)).all()
    return list(paginated), total
