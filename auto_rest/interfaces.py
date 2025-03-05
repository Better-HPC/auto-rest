"""Pydantic models are used to facilitate data validation and to define
interfaces for FastAPI endpoint handlers. The `interfaces` module
provides utility functions for converting SQLAlchemy models into
Pydantic interfaces.
"""

from typing import Any, Callable, Iterator

from pydantic import BaseModel as PydanticModel, create_model
from sqlalchemy import Column, Table

__all__ = ["create_interface", "create_optional_interface", "create_pk_interface"]


def iter_columns(table: Table, pk_only: bool = False) -> Iterator[Column]:
    """Iterate over the columns of a SQLAlchemy model.

    Args:
        table: The table to iterate columns over.
        pk_only: If True, only iterate over primary key columns.

    Yields:
        A column of the SQLAlchemy model.
    """

    for column in table.columns.values():
        if column.primary_key or not pk_only:
            yield column


def get_col_type(col: Column) -> type[any]:
    """Determine the Python type corresponding to a SQLAlchemy column.

    Some database drivers do not support type casting to native Python types.
    In these cases, the `Any` type is returned instead.

    Args:
        col: The SQLAlchemy column to get the type for.

    Returns:
        The equivalent Python type for the column.
    """

    try:
        col_type = col.type.python_type

    except NotImplementedError:
        return Any

    if col.nullable or col.default or col.server_default:
        col_type |= None

    return col_type


def get_col_default(col: Column) -> any:
    """Retrieve the default value for a SQLAlchemy column.

    Args:
        col: The SQLAlchemy column to get the default value for.

    Returns:
        The default value of the column.
    """

    # SQLAlchemy employs two mechanisms for storing defaults.
    # Make a good faith effort to parse server side (SQL) defaults but
    # fall back to Python side defaults, which defaults to `None`.
    server_default = getattr(col.server_default, "arg", col.server_default)
    python_default = getattr(col.default, "arg", col.default)

    try:
        if isinstance(server_default, Callable):
            return server_default

        elif col.server_default is not None:
            server_default = str(server_default).strip("'").strip('"')
            return col.type.python_type(server_default)

    # NotImplementedError: Python typing not supported by the database driver
    # ValueError: Tried and failed to cast server default into Python object
    # Exception: Unexpected error due to edge case with unknown cause
    except (NotImplementedError, ValueError, Exception):
        pass

    return python_default


def create_pk_interface(table: Table) -> type[PydanticModel]:
    """Create a Pydantic model representing the primary key columns of a SQLAlchemy table.

    Args:
        table: The SQLAlchemy table to generate the Pydantic model for.

    Returns:
        A Pydantic model class where each field corresponds to a primary key column.
    """

    fields = {
        col.name: (get_col_type(col), ...)
        for col in iter_columns(table, pk_only=True)
    }

    return create_model(f"{table.name}-PK", __config__={'arbitrary_types_allowed': True}, **fields)


def create_optional_interface(table: Table) -> type[PydanticModel]:
    """Create a Pydantic model representing all columns of a SQLAlchemy table with nullable types.

    Args:
        table: The SQLAlchemy table to generate the Pydantic model for.

    Returns:
        A Pydantic model class where each field corresponds to a column, with nullable types.
    """

    fields = {
        col.name: (get_col_type(col) | None, get_col_default(col))
        for col in iter_columns(table)
    }

    return create_model(f"{table.name}-Optional", __config__={'arbitrary_types_allowed': True}, **fields)


def create_interface(table: Table) -> type[PydanticModel]:
    """Create a Pydantic model representing all columns of a SQLAlchemy table with default values.

    Args:
        table: The SQLAlchemy table to generate the Pydantic model for.

    Returns:
        A Pydantic model class where each field corresponds to a column, with default values if available.
    """

    fields = {
        col.name: (get_col_type(col), get_col_default(col))
        for col in iter_columns(table)
    }

    return create_model(f"{table.name}", __config__={'arbitrary_types_allowed': True}, **fields)
