"""Pydantic models are used to facilitate data validation and to define
interfaces for FastAPI endpoint handlers. The `interfaces` module
provides utility functions for converting SQLAlchemy models into
Pydantic interfaces. Interfaces can be created using different modes
which force interface fields to be optional or read only.

!!! example "Example: Creating an Interface"

    The `create_interface_default` method creates an interface class
    based on a SQLAlchemy table.

    ```python
    default_interface = create_interface_default(database_model)
    required_interface = create_interface_required(database_model, mode="required")
    optional_interface = create_interface_optional(database_model, mode="optional")
    ```
"""
from typing import Iterator, Literal

from pydantic import BaseModel as PydanticModel, create_model
from sqlalchemy import Column, Table

__all__ = ["create_interface"]

from sqlalchemy.sql.schema import ScalarElementColumnDefault

MODES = Literal["default", "required", "optional"]


def iter_columns(table: Table, pk_only: bool = False) -> Iterator[Column]:
    """Iterate over the columns of a SQLAlchemy model.

    Args:
        table: The table to iterate columns over.
        pk_only: If True, only iterate over primary key columns.

    Yields:
        A column of the SQLAlchemy model.
    """

    for column in table.columns:
        if column.primary_key or not pk_only:
            yield column


def get_column_type(col: Column) -> type[any]:
    """Return the Python type corresponding to a column's DB datatype.

    Returns the `any` type for DBMS drivers that do not support mapping DB
    types to Python primitives,

    Args:
        col: The column to determine a type for.

    Returns:
        The equivalent Python type for the column data.
    """

    try:
        return col.type.python_type

    # Catch any error, but list the expected ones explicitly
    except (NotImplementedError, Exception):
        return any


def get_column_default(col: Column, mode: MODES) -> any:
    """Return the default value for a column.

    Args:
        col: The column to determine a default value for.
        mode: The mode to use when determining the default value.

    Returns:
        The default value for the column.
    """

    # Extract the default value from the SQLAlchemy wrapper class
    sqla_default = col.default
    default = getattr(sqla_default, "arg", None) or sqla_default

    if mode == "required":
        return ...

    elif mode == "optional":
        return default

    elif mode == "default":
        if col.nullable or (col.default is not None):
            return default

        return ...

    raise RuntimeError(f"Unknown mode: {mode}")


def create_interface(
    table: Table,
    pk_only: bool = False,
    mode: MODES = "default"
) -> type[PydanticModel]:
    """Create a Pydantic interface for a SQLAlchemy model where all fields are required.

    Args:
        table: The SQLAlchemy table to create an interface for.
        pk_only: If True, only include primary key columns.
        mode: Whether to force fields to all be optional or required.

    Returns:
        A dynamically generated Pydantic model with all fields required.
    """

    # Map field names to the column type and default value.
    columns = iter_columns(table, pk_only)
    fields = {
        col.name: (get_column_type(col), get_column_default(col, mode))
        for col in columns
    }

    # Dynamically create a unique name for the interface
    name_parts = [table.name, mode.title()]
    if pk_only:
        name_parts.insert(1, 'PK')

    interface_name = '-'.join(name_parts)
    return create_model(interface_name, **fields)
