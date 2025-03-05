from datetime import datetime
from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, PropertyMock

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from auto_rest.interfaces import get_col_type


class TestGetColumnType(TestCase):
    """Unit tests for the `get_col_type` method."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create dummy table columns with a mix of types and nullabilities."""

        # Columns with different types
        cls.col_str = Column("str_col", String, nullable=False)
        cls.col_int = Column("int_col", Integer, nullable=False)
        cls.col_flt = Column("flt_col", Float, nullable=False)
        cls.col_txt = Column("txt_col", Text, nullable=False)
        cls.col_dtm = Column("dtm_col", DateTime, nullable=False)

        # Columns with varying nullability
        cls.col_str_nullable = Column("str_col", String, nullable=True)

    def test_column_types(self) -> None:
        """Verify the function returns the expected types for different column types."""

        # Verify behavior for a handful of common types
        self.assertEqual(str, get_col_type(self.col_str))
        self.assertEqual(int, get_col_type(self.col_int))
        self.assertEqual(float, get_col_type(self.col_flt))
        self.assertEqual(str, get_col_type(self.col_txt))
        self.assertEqual(datetime, get_col_type(self.col_dtm))

        # Verify behavior with nullable columns
        self.assertEqual(str | None, get_col_type(self.col_str_nullable))

    def test_missing_driver_support(self) -> None:
        """Verify the returned type defaults to `Any` when type casting is not supported by the driver."""

        # Mock a column
        mock_col = MagicMock(spec=Column)
        mock_col.nullable = False
        mock_col.default = None

        # Mock a `NotImplementedError` error being thrown by the DB driver.
        type(mock_col.type).python_type = PropertyMock(side_effect=NotImplementedError)

        self.assertEqual(Any, get_col_type(mock_col))
