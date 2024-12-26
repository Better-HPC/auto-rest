"""Injectable dependencies and utility functions used for building FastAPI request handlers."""

from typing import Literal

from fastapi import Query
from sqlalchemy import asc, desc
from sqlalchemy.sql.selectable import Select
from starlette.responses import Response

__all__ = [
    "apply_ordering_params",
    "apply_pagination_params",
    "get_ordering_params",
    "get_pagination_params",
]


def get_pagination_params(
    _limit_: int = Query(10, ge=0, description="The maximum number of records to return."),
    _offset_: int = Query(0, ge=0, description="The starting index of the returned records."),
) -> dict[str, int]:
    """Extract pagination parameters from request query parameters.

    Args:
        _limit_: The maximum number of records to return.
        _offset_: The starting index of the returned records.

    Returns:
        dict: A dictionary containing the `limit` and `offset` values.
    """

    return {"limit": _limit_, "offset": _offset_}


def apply_pagination_params(query: Select, params: dict[str, int], response: Response) -> Select:
    """Apply pagination to a database query.

    Returns a copy of the provided query with offset and limit parameters applied.
    Intended for use with parameters returned by the `get_pagination_params` dependency.

    Args:
        query: The database query to apply parameters to.
        params: A dictionary containing parsed URL parameters.
        response: The outgoing HTTP response object.

    Returns:
        A copy of the query modified to only return the paginated values.
    """

    limit = params["limit"]
    offset = params["offset"]
    return query.offset(offset).limit(limit)


def get_ordering_params(
    _order_by_: str | None = Query(None, description="Field name to sort by."),
    _direction_: Literal["asc", "desc"] = Query("asc", description="Sort results in 'asc' or 'desc' order.")
) -> dict:
    """Extract ordering parameters from request query parameters.

    Args:
        _order_by_: The field to order by.
        _direction_: The direction to order by.

    Returns:
        dict: A dictionary containing the `order_by` and `direction` values.
    """

    return {"order_by": _order_by_, "direction": _direction_}


def apply_ordering_params(query: Select, params: dict, response: Response) -> Select:
    """Apply ordering to a database query.

    Returns a copy of the provided query with ordering parameters applied.
    Intended for use with parameters returned by the `get_ordering_params` dependency.

    Args:
        query: The database query to apply parameters to.
        params: A dictionary containing parsed URL parameters.
        response: The outgoing HTTP response object.

    Returns:
        A copy of the query modified to return ordered values.
    """

    order_by = params.get("order_by")
    direction = params.get("direction")

    if not order_by:
        return query  # No ordering requested

    sort_func = desc if direction == "desc" else asc
    return query.order_by(sort_func(order_by))
