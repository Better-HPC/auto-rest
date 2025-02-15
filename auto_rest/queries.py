"""
The `queries` module provides asynchronous wrapper functions around operations
involving SQLAlchemy sessions. These utilities automatically account for
variations in behavior between synchronous and asynchronous session types
(i.e., `Session` and `AsyncSession` instances). This ensures consistent query
handling and provides a streamlined interface for database interactions.

!!! example "Example: Query Execution"

    Query utilities seamlessly support synchronous and asynchronous session types.

    ```python
    query = select(SomeTable).where(SomeTable.id == item_id)

    with Session(...) as sync_session:
        result = await execute_session_query(sync_session, query)

    with AsyncSession(...) as async_session:
        result = await execute_session_query(async_session, query)
    ```
"""

import logging
from typing import Literal

from fastapi import HTTPException
from sqlalchemy import asc, desc, Executable, Result, Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auto_rest.models import DBSession

__all__ = [
    "apply_ordering_params",
    "apply_pagination_params",
    "commit_session",
    "delete_session_record",
    "execute_session_query",
    "get_record_or_404"
]

logger = logging.getLogger("auto_rest.query")


def apply_ordering_params(
    query: Select,
    order_by: str | None = None,
    direction: Literal["desc", "asc"] = "asc"
) -> Select:
    """Apply ordering to a database query.

    Returns a copy of the provided query with ordering parameters applied.

    Args:
        query: The database query to apply parameters to.
        order_by: The name of the column to order by.
        direction: The direction to order by (defaults to "asc").

    Returns:
        A copy of the query modified to return ordered values.
    """

    if order_by is None:
        return query

    if order_by not in query.columns:
        raise ValueError(f"Invalid column name: {order_by}")

    # Default to ascending order for an invalid ordering direction
    if direction == "desc":
        return query.order_by(desc(order_by))

    elif direction == "asc":
        return query.order_by(asc(order_by))

    raise ValueError(f"Invalid direction, use 'asc' or 'desc': {direction}")


def apply_pagination_params(query: Select, limit: int = 0, offset: int = 0) -> Select:
    """Apply pagination to a database query.

    Returns a copy of the provided query with offset and limit parameters applied.

    Args:
        query: The database query to apply parameters to.
        limit: The number of results to return.
        offset: The offset to start with.

    Returns:
        A copy of the query modified to only return the paginated values.
    """

    if offset < 0 or limit < 0:
        raise ValueError("Pagination parameters cannot be negative")

    # Do not apply pagination if not requested
    if limit == 0:
        return query

    return query.offset(offset or 0).limit(limit)


async def commit_session(session: DBSession) -> None:
    """Commit a SQLAlchemy session.

    Supports synchronous and asynchronous sessions.

    Args:
        session: The session to commit.
    """

    if isinstance(session, AsyncSession):
        await session.commit()

    else:
        session.commit()


async def delete_session_record(session: DBSession, record: Result) -> None:
    """Delete a record from the database using an existing session.

    Does not automatically commit the session.
    Supports synchronous and asynchronous sessions.

    Args:
        session: The session to use for deletion.
        record: The record to be deleted.
    """

    logger.debug("Deleting record.")
    if isinstance(session, AsyncSession):
        await session.delete(record)

    else:
        session.delete(record)


async def execute_session_query(session: DBSession, query: Executable) -> Result:
    """Execute a query in the given session and return the result.

    Supports synchronous and asynchronous sessions.

    Args:
        session: The SQLAlchemy session to use for executing the query.
        query: The query to be executed.

    Returns:
        The result of the executed query.
    """

    logger.debug(str(query).replace("\n", " "))
    if isinstance(session, AsyncSession):
        return await session.execute(query)

    return session.execute(query)


def get_record_or_404(result: Result) -> any:
    """Retrieve a scalar record from a query result or raise a 404 error.

    Args:
        result: The query result to extract the scalar record from.

    Returns:
        The scalar record if it exists.

    Raises:
        HTTPException: If the record is not found.
    """

    if record := result.fetchone():
        return record

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
