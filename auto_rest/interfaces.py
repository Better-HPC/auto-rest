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

    # Some DBMS drivers do not support mapping DB types to Python primitives
    try:
        col_type = col.type.python_type

    except NotImplementedError:
        return any

    # Adjust type hinting to reflect optional columns
    if col.nullable or col.autoincrement:
        col_type |= None

    return col_type


def get_column_default(col: Column, mode: str) -> any:

    # Check whether the column has a predefined or dynamic default value
    has_default_behavior = (col.default is not None) or col.nullable or bool(col.autoincrement)

    return {
        "required": ...,
        "optional": None,
        "default": col.default if has_default_behavior else ...,
    }[mode]


def create_interface(
    table: Table,
    pk_only: bool = False,
    mode: Literal["default", "required", "optional"] = "default"
) -> type[PydanticModel]:
    """Create a Pydantic interface for a SQLAlchemy model where all fields are required.

    Args:
        table: The SQLAlchemy table to create an interface for.
        pk_only: If True, only include primary key columns.
        mode: Whether to force fields to all be optional or required.

    Returns:
        A dynamically generated Pydantic model with all fields required.
    """

    columns = iter_columns(table, pk_only)
    fields = {
        col.name: (get_column_type(col), get_column_default(col, mode))
        for col in columns
    }

    return create_model(table.name, **fields)
