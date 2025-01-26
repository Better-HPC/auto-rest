"""Pydantic models are used to facilitate data validation and to define
interfaces for FastAPI endpoint handlers. The `interfaces` module
provides utility functions for converting SQLAlchemy models into
Pydantic interfaces. Dedicated utilities are provided for creating
with varying levels of constraints on the generated interface fields.

!!! example "Example: Creating an Interface"

    The `create_interface_default` method creates an interface class where
    fields are marked as required based on whether they are required in
    the database model.  Other methods can be used to generate interfaces
    where all fields are required or optional.

    ```python
    default_interface = create_interface_default(database_model)
    required_interface = create_interface_required(database_model)
    optional_interface = create_interface_optional(database_model)
    ```
"""

from typing import Iterator, Literal

from pydantic import BaseModel as PydanticModel, create_model
from sqlalchemy import Column, Table

__all__ = ["create_interface"]

MODES = Literal["default", "required", "optional"]


def iter_columns(table: Table, pk_only: bool) -> Iterator[Column]:
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

    except NotImplementedError:
        return any


def get_column_default(col: Column, mode: MODES) -> any:
    """Return the default value for a column.

     Modes:
        - "required": All fields are required, and no default values are used.
        - "optional": All fields are optional, and `None` is the default value.
        - "default": Fields are required based on the column's `nullable` property.

    Args:
        col: The column to determine a default value for.
        mode: The mode to use when determining the default value.

    Returns:
        The default value for the column.
    """

    # Check whether the column has a predefined or dynamic default value
    has_default_value = (col.default is not None) or col.nullable

    return {
        "required": ...,
        "optional": None,
        "default": col.default if has_default_value else ...,
    }[mode]


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

    # Map field names to the column type and default.
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
