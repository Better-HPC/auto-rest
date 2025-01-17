"""
The `params` module provides utilities for extracting and applying query
parameters from incoming HTTP requests. These utilities ensure the consistent
parsing, validation, and application of query parameters, and automatically
update HTTP response headers to reflect applied query options.

Parameter functions are designed in pairs. A *get* function is used to parse
parameters from a FastAPI request and an *apply* function is used to apply
the arguments onto a SQLAlchemy query.

!!! example "Example: Parameter Parsing and Application"

    When handling URL parameters, a *get* function is injected as a dependency
    into the signature of the request handler. The parsed parameter dictionary
    is then passed to an *apply* function.

    ```python
    from fastapi import FastAPI, Response, Depends
    from sqlalchemy import select
    from auto_rest.query_params import get_pagination_params, apply_pagination_params

    app = FastAPI()

    @app.get("/items/")
    async def list_items(
        pagination_params: dict = Depends(get_pagination_params),
        response: Response
    ):
        query = select(SomeModel)
        query = apply_pagination_params(query, pagination_params, response)
        return ...  # Logic to further process and execute the query goes here
    ```
"""

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
    Compatible with parameters returned by the `get_pagination_params` method.

    Args:
        query: The database query to apply parameters to.
        params: A dictionary containing parsed URL parameters.
        response: The outgoing HTTP response object.

    Returns:
        A copy of the query modified to only return the paginated values.
    """

    limit = params.get("limit", 0)
    offset = params.get("offset", 0)

    response.headers["X-Pagination-Limit"] = str(limit)
    response.headers["X-Pagination-Offset"] = str(offset)
    if limit <= 0 or offset < 0:
        response.headers["X-Pagination-Applied"] = "false"
        return query

    response.headers["X-Pagination-Applied"] = "true"
    return query.offset(offset).limit(limit)


def get_ordering_params(
    _order_by_: str | None = Query(None, description="The field name to sort by."),
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
    Compatible with parameters returned by the `get_ordering_params` method.

    Args:
        query: The database query to apply parameters to.
        params: A dictionary containing parsed URL parameters.
        response: The outgoing HTTP response object.

    Returns:
        A copy of the query modified to return ordered values.
    """

    order_by = params.get("order_by")
    direction = params.get("direction", "asc")

    response.headers["X-Order-By"] = order_by
    response.headers["X-Order-Direction"] = direction
    if order_by not in query.columns.keys():
        response.headers["X-Order-Applied"] = "false"
        return query

    if direction == "asc":
        return query.order_by(asc(order_by))

    if direction == "desc":
        return query.order_by(desc(order_by))

    raise ValueError("Ordering direction must be 'asc' or 'desc'.")
