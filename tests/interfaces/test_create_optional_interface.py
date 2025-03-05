import unittest

from sqlalchemy import Column, Integer, MetaData, Table, Text

from auto_rest.interfaces import create_optional_interface


class TestCreateOptionalInterface(unittest.TestCase):
    """Unit tests for the `create_optional_interface` method."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create a new Pydantic interface from a dummy Sqlalchemy table."""

        cls.table = Table(
            "test_model", MetaData(),
            Column("id1", Integer, primary_key=True),
            Column("id2", Integer, primary_key=True),
            Column("str_nul", Text, nullable=True),
            Column("str_req", Text, nullable=False),
        )

        cls.interface = create_optional_interface(cls.table)

    def test_field_types(self) -> None:
        """Verify the interface includes correctly typed fields for all columns."""

        self.assertEqual(int | None, self.interface.__annotations__["id1"])
        self.assertEqual(int | None, self.interface.__annotations__["id2"])
        self.assertEqual(str | None, self.interface.__annotations__["str_nul"])
        self.assertEqual(str | None, self.interface.__annotations__["str_req"])

    def test_field_defaults(self) -> None:
        """Verify all fields are marked as optional with correct default values."""

        self.assertEqual(None, self.interface.model_fields["id1"].default)
        self.assertEqual(None, self.interface.model_fields["id2"].default)
        self.assertEqual(None, self.interface.model_fields["str_nul"].default)
        self.assertEqual(None, self.interface.model_fields["str_req"].default)
