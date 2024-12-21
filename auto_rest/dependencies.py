"""Injectable dependencies and utility functions used for building FastAPI request handlers."""

import logging
from typing import Callable, Literal

from fastapi import Query
from sqlalchemy import asc, desc, Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.query import Query as DBQuery
from starlette.responses import Response

from .models import ModelBase

__all__ = [
    "create_db_dependency",
    "apply_ordering_params",
    "apply_pagination_params",
    "get_ordering_params",
    "get_pagination_params",
]


def create_db_dependency(conn_pool: Engine) -> Callable[[], Session]:
    """Factory function for a FastAPI dependency that generates new database sessions.

    Args:
        conn_pool: Connection pool to generate new sessions from.

    Returns:
        A function that yields new database session.
    """

    session_factory = sessionmaker(bind=conn_pool, autocommit=False, autoflush=False)

    def get_db_session() -> Session:
        """Yield a new database session."""

        logging.debug("Fetching database session.")
        with session_factory() as session:
            yield session

    return get_db_session


def get_pagination_params(
    _page_: int = Query(0, description="Page number."),
    _per_page_: int = Query(10, gt=0, description="Items per page."),
) -> dict[str, int]:
    """Extract pagination parameters from request query parameters.

    Args:
        _page_: The page number.
        _per_page_: The number of items per page.

    Returns:
        dict: A dictionary containing the `page` and `per_page` values.
    """

    return {"page": _page_, "per_page": _per_page_}


def apply_pagination_params(
    items: list[any],
    pagination: dict[str, int],
    response: Response,
) -> list[any]:
    """Paginate a list of items and set metadata in response headers.

    Intended for use with parameters returned by the `get_pagination_params` dependency.
    Pagination is disabled and all values are returned when the page number is zero.
    Negative page numbers correspond to pages counted from the end.

    Args:
        items: The list of items to paginate.
        pagination: A dictionary containing the `page` and `per_page` parameters.
        response: Optionally add pagination headers to an HTTP response object.

    Returns:
        A slice of the original list containing the paginated items.
    """

    page = pagination["page"]
    per_page = pagination["per_page"]

    if per_page <= 0:
        raise ValueError('The `per_page` argument must be greater than 0.')

    total_count = len(items)
    total_pages = (total_count + per_page - 1) // per_page

    # Calculate start and end indices
    if page == 0:
        return items

    elif page > 0:
        start = (page - 1) * per_page
        end = start + per_page

    else:
        start = (total_pages + page) * per_page
        end = start + per_page

    # Add pagination metadata to response headers
    response.headers["x-page"] = str(page)
    response.headers["x-per-page"] = str(per_page)
    response.headers["x-total-pages"] = str(total_pages)
    response.headers["x-total-count"] = str(total_count)
    return items[start:end]


def get_ordering_params(
    _order_by_: str | None = Query(None, description="Field to sort by"),
    _direction_: Literal["asc", "desc"] = Query("asc", description="Sort direction must be 'asc' or 'desc'")
) -> dict:
    """Extract ordering parameters from request query parameters.

    Args:
        _order_by_: The field to order by.
        _direction_: The direction to order by.

    Returns:
        dict: A dictionary containing the `order_by` and `direction` values.
    """

    return {"order_by": _order_by_, "direction": _direction_}


def apply_ordering_params(query: DBQuery, db_model: ModelBase, ordering_params: dict) -> DBQuery:
    """Return a copy of a sqlalchemy query with ordering applied.

    Intended for use with parameters returned by the `get_ordering_params` dependency.
    If ordering is requested using a column name not found in the given table,
    ordering is not applied and the function will exit silently.

    Args:
        query: The sqlalchemy query.
        db_model: The database model whose column is being sorted.
        ordering_params: A dictionary containing the `order_by` and `direction` parameters.

    Returns:
        An ordered database query
    """

    order_by = ordering_params.get("order_by")
    direction = ordering_params.get("direction")

    if not order_by:
        return query  # No ordering requested

    try:
        sort_field = getattr(db_model, order_by)

    except AttributeError:
        return query

    sort_func = desc if direction == "desc" else asc
    return query.order_by(sort_func(sort_field))
