from unittest import TestCase

from sqlalchemy import Column, String

from auto_rest.interfaces import create_field


class TestCreateField(TestCase):
    """Unit tests for the `create_field` method."""

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

        returned_nullable = create_field(self.col_nullable, mode="default")
        returned_required = create_field(self.col_required, mode="default")
        returned_nullable_default = create_field(self.col_nullable_default, mode="default")
        returned_required_default = create_field(self.col_required_default, mode="default")

        self.assertIs(returned_nullable, None)
        self.assertIs(returned_required, ...)
        self.assertEqual("default", returned_nullable_default)
        self.assertEqual("default", returned_required_default)

    def test_required_mode(self) -> None:
        """Verify returned values in `required` mode.

        In `required` mode, all columns are required regardless of the column schema.
        `...` is used by the application to indicate required interface fields.
        """

        returned_nullable = create_field(self.col_nullable, mode="required")
        returned_required = create_field(self.col_required, mode="required")
        returned_nullable_default = create_field(self.col_nullable_default, mode="required")
        returned_required_default = create_field(self.col_required_default, mode="required")

        self.assertIs(returned_nullable, ...)
        self.assertIs(returned_required, ...)
        self.assertIs(returned_nullable_default, ...)
        self.assertIs(returned_required_default, ...)

    def test_optional_mode(self) -> None:
        """Verify returned values in `required` mode.

        In `optional` mode, all columns are optional regardless of the column schema.
        `None` is used by the application to indicate optional interface fields.
        """

        returned_nullable = create_field(self.col_nullable, mode="optional")
        returned_required = create_field(self.col_required, mode="optional")
        returned_nullable_default = create_field(self.col_nullable_default, mode="optional")
        returned_required_default = create_field(self.col_required_default, mode="optional")

        self.assertIsNone(returned_nullable)
        self.assertIsNone(returned_required)
        self.assertEqual("default", returned_nullable_default)
        self.assertEqual("default", returned_required_default)

    def test_unknown_mode(self) -> None:
        """Verify a `RuntimeError` error is raised for an unknown mode argument."""

        with self.assertRaises(RuntimeError):
            create_field(self.col_nullable, mode="not a mode")