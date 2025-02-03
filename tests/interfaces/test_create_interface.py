import unittest
from datetime import date

from pydantic_core import PydanticUndefined
from sqlalchemy import Column, Date, Float, Integer, MetaData, String, Table

from auto_rest.interfaces import create_interface


class TestCreateInterface(unittest.TestCase):
    """Unit tests for the `create_interface` method."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create a dummy database table to generate interfaces from."""

        cls.table = Table(
            "test_model", MetaData(),
            Column("id1", Integer, primary_key=True),
            Column("id2", Integer, primary_key=True),
            Column("str_col", String),
            Column("float_col", Float, default=5),
            Column("date_col", Date, default=date.today),
        )

    def test_fields(self) -> None:
        """Verify the interface includes correctly typed fields for all columns."""

        interface = create_interface(self.table)
        self.assertCountEqual(["id1", "id2", "str_col", "float_col", "date_col"], interface.model_fields.keys())

        self.assertEqual(interface.__annotations__["id1"], int)
        self.assertEqual(interface.__annotations__["id2"], int)
        self.assertEqual(interface.__annotations__["str_col"], str)
        self.assertEqual(interface.__annotations__["float_col"], float)
        self.assertEqual(interface.__annotations__["date_col"], date)

    def test_pk_only_fields(self) -> None:
        """Verify the interface only includes primary key columns when `pk_only` is enabled."""

        interface = create_interface(self.table, pk_only=True)
        self.assertCountEqual(["id1", "id2"], interface.model_fields.keys())
        self.assertEqual(interface.__annotations__["id1"], int)
        self.assertEqual(interface.__annotations__["id2"], int)

    def test_defaults(self) -> None:
        """Verify default field values match the input table."""

        interface = create_interface(self.table)
        self.assertEqual(PydanticUndefined, interface.model_fields["id1"].default)
        self.assertEqual(PydanticUndefined, interface.model_fields["id2"].default)
        self.assertEqual(None, interface.model_fields["str_col"].default)
        self.assertEqual(5, interface.model_fields["float_col"].default)
        self.assertEqual(date.today(), interface.model_fields["date_col"].default(None))

    def test_required_mode_defaults(self) -> None:
        """Verify all fields are marked as required in `required` mode."""

        interface = create_interface(self.table, mode="required")
        for col in self.table.columns:
            self.assertEqual(PydanticUndefined, interface.model_fields[col.name].default)

    def test_optional_mode_defaults(self) -> None:
        """Verify all fields are marked as optional with correct defaults in `optional` mode."""

        interface = create_interface(self.table, mode="optional")
        self.assertEqual(None, interface.model_fields["id1"].default)
        self.assertEqual(None, interface.model_fields["id2"].default)
        self.assertEqual(None, interface.model_fields["str_col"].default)
        self.assertEqual(5, interface.model_fields["float_col"].default)
        self.assertEqual(date.today(), interface.model_fields["date_col"].default(None))
