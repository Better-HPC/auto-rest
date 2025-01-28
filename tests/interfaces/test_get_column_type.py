from datetime import date, datetime, time
from decimal import Decimal
from unittest import TestCase
from unittest.mock import MagicMock, PropertyMock

from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import *

from auto_rest.interfaces import get_column_type


class TestGetColumnType(TestCase):
    """Unit tests for the `get_column_type` method."""

    def test_returned_types(self) -> None:
        """Verify returned types match the table definitions."""

        expected_types = {
            # Primary key columns
            Column("pk_col", String): str,
            Column("pk_col", String, nullable=False): str,
            Column("pk_col", String, nullable=True): str,

            # Non-nullable columns for various SQLAlchey column types
            Column("bool_col", Boolean, nullable=False): bool,
            Column("str_col", String, nullable=False): str,
            Column("text_col", Text, nullable=False): str,
            Column("unicode_col", Unicode, nullable=False): str,
            Column("unicode_text_col", UnicodeText, nullable=False): str,
            Column("int_col", Integer, nullable=False): int,
            Column("small_int_col", SmallInteger, nullable=False): int,
            Column("big_int_col", BigInteger, nullable=False): int,
            Column("float_col", Float, nullable=False): float,
            Column("numeric_col", Numeric, nullable=False): Decimal,
            Column("double_col", Double, nullable=False): float,
            Column("datetime_col", DateTime, nullable=False): datetime,
            Column("date_col", Date, nullable=False): date,
            Column("time_col", Time, nullable=False): time,
            Column("binary_col", LargeBinary, nullable=False): bytes,
            Column("enum_col", Enum, nullable=False): str,
            Column("pickle_col", PickleType, nullable=False): any,
            Column("array_col", ARRAY(String), nullable=False): list,
            Column("json_col", JSON, nullable=False): dict,

            # Nullable columns
            Column("null_str_col", String, nullable=True): str,
            Column("null_int_col", Integer, nullable=True): int,
            Column("null_float_col", Float, nullable=True): float,
        }

        for test_column, expected_type in expected_types.items():
            returned_type = get_column_type(test_column)
            self.assertIs(returned_type, expected_type, f"Incorrect type for column {test_column.name}")

    def test_missing_driver_support(self) -> None:
        """Verify the returned type defaults to `any` when type casting is not supported by the driver."""

        # Mock a `NotImplementedError` error being thrown by the DB driver.
        mock_col = MagicMock(spec=Column)
        type(mock_col.type).python_type = PropertyMock(side_effect=NotImplementedError)

        returned_type = get_column_type(mock_col)
        self.assertIs(any, returned_type)
