from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, PropertyMock

from sqlalchemy import Column, String

from auto_rest.interfaces import create_field_definition


class TestCreateField(TestCase):
    """Unit tests for the `create_field_definition` method."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create dummy table columns with a mix of types and nullabilities."""

        # (Non)nullable columns without default values
        cls.col_nullable = Column("str_col", String, nullable=True)
        cls.col_required = Column("str_col", String, nullable=False)

        # (Non)nullable columns with default values
        cls.col_nullable_default = Column("str_col", String, default="default", nullable=True)
        cls.col_required_default = Column("str_col", String, default="default", nullable=False)

    def test_default_mode(self) -> None:
        """Verify returned values in `default` mode.

        In `default` mode, returned values match the underlying database schema.
        """

        returned_nullable = create_field_definition(self.col_nullable, mode="default")
        returned_required = create_field_definition(self.col_required, mode="default")
        returned_nullable_default = create_field_definition(self.col_nullable_default, mode="default")
        returned_required_default = create_field_definition(self.col_required_default, mode="default")

        self.assertEqual((str | None, None), returned_nullable)
        self.assertEqual((str, ...), returned_required)
        self.assertEqual((str | None, 'default'), returned_nullable_default)
        self.assertEqual((str | None, 'default'), returned_required_default)

    def test_required_mode(self) -> None:
        """Verify returned values in `required` mode.

        In `required` mode, all columns are required regardless of the column schema.
        `...` is used by the application to indicate required interface fields.
        """

        returned_nullable = create_field_definition(self.col_nullable, mode="required")
        returned_required = create_field_definition(self.col_required, mode="required")
        returned_nullable_default = create_field_definition(self.col_nullable_default, mode="required")
        returned_required_default = create_field_definition(self.col_required_default, mode="required")

        self.assertEqual((str, ...), returned_nullable)
        self.assertEqual((str, ...), returned_required)
        self.assertEqual((str, ...), returned_nullable_default)
        self.assertEqual((str, ...), returned_required_default)

    def test_optional_mode(self) -> None:
        """Verify returned values in `required` mode.

        In `optional` mode, all columns are optional regardless of the column schema.
        `None` is used by the application to indicate optional interface fields.
        """

        returned_nullable = create_field_definition(self.col_nullable, mode="optional")
        returned_required = create_field_definition(self.col_required, mode="optional")
        returned_nullable_default = create_field_definition(self.col_nullable_default, mode="optional")
        returned_required_default = create_field_definition(self.col_required_default, mode="optional")

        self.assertEqual((str | None, None), returned_nullable)
        self.assertEqual((str | None, None), returned_required)
        self.assertEqual((str | None, 'default'), returned_nullable_default)
        self.assertEqual((str | None, 'default'), returned_required_default)

    def test_unknown_mode(self) -> None:
        """Verify a `RuntimeError` error is raised for an unknown mode argument."""

        with self.assertRaises(RuntimeError):
            create_field_definition(self.col_nullable, mode="not a mode")

    def test_missing_driver_support(self) -> None:
        """Verify the returned type defaults to `Any` when type casting is not supported by the driver."""

        # Mock a column
        mock_col = MagicMock(spec=Column)
        mock_col.nullable = False
        mock_col.default = None

        # Mock a `NotImplementedError` error being thrown by the DB driver.
        type(mock_col.type).python_type = PropertyMock(side_effect=NotImplementedError)

        self.assertEqual((Any, ...), create_field_definition(mock_col))
