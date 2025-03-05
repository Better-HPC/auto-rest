from unittest import TestCase

import sqlalchemy.sql.functions
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, text
from sqlalchemy.sql import func

from auto_rest.interfaces import get_col_default


class TestGetColDefault(TestCase):
    """Unit tests for the `get_col_default` method."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create dummy table columns with a mix of types and nullabilities."""

        # Column without default values
        cls.col_no_default = Column("str_col", String, nullable=True)

        # Columns with static default values
        cls.col_default_str = Column("str_col", String, default="default_value")
        cls.col_default_int = Column("int_col", Integer, default=42)
        cls.col_default_bool = Column("bool_col", Boolean, default=True)
        cls.col_default_float = Column("float_col", Float, default=3.14)

        # Columns with callable default values
        cls.col_default_func = Column("timestamp_col", DateTime, default=func.now())

        # Columns with server-side defaults (database-managed)
        cls.col_server_default_text = Column("text_col", String, server_default=text("'server_default'"))
        cls.col_server_default_int = Column("int_col", Integer, server_default=text("100"))
        cls.col_server_default_bool = Column("bool_col", Boolean, server_default=text("TRUE"))
        cls.col_server_default_float = Column("float_col", Float, server_default=text("2.718"))

        # Server-side timestamp function default
        cls.col_server_default_func = Column("timestamp_col", DateTime, server_default=func.now())

    def test_no_default_value(self) -> None:
        """Verify columns with no default value return `None`."""
        self.assertIsNone(get_col_default(self.col_no_default))

    def test_static_defaults(self) -> None:
        """Verify columns with predefined static default values return the value."""

        self.assertEqual("default_value", get_col_default(self.col_default_str))
        self.assertEqual(42, get_col_default(self.col_default_int))
        self.assertEqual(True, get_col_default(self.col_default_bool))
        self.assertEqual(3.14, get_col_default(self.col_default_float))

    def test_callable_defaults(self) -> None:
        """Verify columns with callable default values return the callable."""

        default_func_value = get_col_default(self.col_default_func)
        self.assertIsInstance(default_func_value, sqlalchemy.sql.functions.now)

    def test_server_static_defaults(self) -> None:
        """Verify columns with server-side static defaults return the correct value."""

        self.assertEqual("server_default", get_col_default(self.col_server_default_text))
        self.assertEqual(100, get_col_default(self.col_server_default_int))
        self.assertEqual(True, get_col_default(self.col_server_default_bool))
        self.assertEqual(2.718, get_col_default(self.col_server_default_float))

    def test_server_function_defaults(self) -> None:
        """Verify columns with server-side function defaults return the function."""

        default_func_value = get_col_default(self.col_server_default_func)
        self.assertIsInstance(default_func_value, sqlalchemy.sql.functions.now)
