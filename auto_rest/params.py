"""
The `params` module provides utilities for extracting and applying query
parameters from incoming HTTP requests. These utilities ensure the consistent
parsing, validation, and application of query parameters, and automatically
update HTTP response headers to reflect applied query options.

Parameter functions are designed in pairs of two. The first function is a
factory for creating an injectable FastAPI dependency. The dependency
is used to parse parameters from incoming requests and applies high level
validation against the parsed values. The second function to applies the
validated arguments onto a SQLAlchemy query and returns the updated query.

!!! example "Example: Parameter Parsing and Application"

    ```python
    from fastapi import FastAPI, Response
    from sqlalchemy import select
    from auto_rest.query_params import create_pagination_dependency, apply_pagination_params

    app = FastAPI()

    @app.get("/items/")
    async def list_items(
        pagination_params: dict = create_pagination_dependency(model),
        response: Response
    ):
        query = select(model)
        query = apply_pagination_params(query, pagination_params, response)
        return ...  # Logic to further process and execute the query goes here
    ```
"""

from collections.abc import Callable
from typing import Literal, Optional

from fastapi import Depends, Query
from sqlalchemy import asc, desc, Table
from sqlalchemy.sql.selectable import Select
from starlette.responses import Response

__all__ = [
    "apply_ordering_params",
    "apply_pagination_params",
    "create_ordering_dependency",
    "create_pagination_dependency",
]


def create_ordering_dependency(table: Table) -> Callable[..., dict]:
    """Create an injectable dependency for fetching ordering arguments from query parameters.

    Args:
        table: The database table to create the dependency for.

    Returns:
        An injectable FastAPI dependency.
    """

    columns = tuple(table.columns.keys())

    def get_ordering_params(
        _order_by_: Optional[Literal[*columns]] = Query(None, description="The field name to sort by."),
        _direction_: Optional[Literal["asc", "desc"]] = Query(None, description="Sort results in 'asc' or 'desc' order.")
    ) -> dict:
        """Extract ordering parameters from request query parameters.

        Args:
            _order_by_: The field to order by.
            _direction_: The direction to order by.

        Returns:
            dict: A dictionary containing the `order_by` and `direction` values.
        """

        return {"order_by": _order_by_, "direction": _direction_}

    return Depends(get_ordering_params)


def apply_ordering_params(query: Select, params: dict, response: Response) -> Select:
    """Apply ordering to a database query.

    Returns a copy of the provided query with ordering parameters applied.
    This method is compatible with parameters returned by the `get_ordering_params` method.
    Ordering is not applied for invalid params, but response headers are still set.

    Args:
        query: The database query to apply parameters to.
        params: A dictionary containing parsed URL parameters.
        response: The outgoing HTTP response object.

    Returns:
        A copy of the query modified to return ordered values.
    """

    order_by = params.get("order_by")
    direction = params.get("direction")

    # Set common response headers
    response.headers["X-Order-By"] = str(order_by)
    response.headers["X-Order-Direction"] = str(direction)

    if order_by is None:
        response.headers["X-Order-Applied"] = "false"
        return query

    # Default to ascending order for an invalid ordering direction
    response.headers["X-Order-Applied"] = "true"
    if direction == "desc":
        return query.order_by(desc(order_by))

    else:
        return query.order_by(asc(order_by))


def create_pagination_dependency(table: Table) -> Callable[..., dict]:
    """Create an injectable dependency for fetching pagination arguments from query parameters.

    Args:
        table: The database table to create the dependency for.

    Returns:
        An injectable FastAPI dependency.
    """

    def get_pagination_params(
        _limit_: Optional[int] = Query(None, ge=0, description="The maximum number of records to return."),
        _offset_: Optional[int] = Query(None, ge=0, description="The starting index of the returned records."),
    ) -> dict[str, int]:
        """Extract pagination parameters from request query parameters.

        Args:
            _limit_: The maximum number of records to return.
            _offset_: The starting index of the returned records.

        Returns:
            dict: A dictionary containing the `limit` and `offset` values.
        """

        return {"limit": _limit_, "offset": _offset_}

    return Depends(get_pagination_params)


def apply_pagination_params(query: Select, params: dict[str, int], response: Response) -> Select:
    """Apply pagination to a database query.

    Returns a copy of the provided query with offset and limit parameters applied.
    This method is compatible with parameters returned by the `get_pagination_params` method.
    Pagination is not applied for invalid params, but response headers are still set.

    Args:
        query: The database query to apply parameters to.
        params: A dictionary containing parsed URL parameters.
        response: The outgoing HTTP response object.

    Returns:
        A copy of the query modified to only return the paginated values.
    """

    limit = params.get("limit")
    offset = params.get("offset")

    # Set common response headers
    response.headers["X-Pagination-Limit"] = str(limit)
    response.headers["X-Pagination-Offset"] = str(offset)

    # Do not apply pagination if not requested
    if limit in (0, None):
        response.headers["X-Pagination-Applied"] = "false"
        return query

    response.headers["X-Pagination-Applied"] = "true"
    return query.offset(offset or 0).limit(limit)
