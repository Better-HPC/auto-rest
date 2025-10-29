import unittest
from datetime import date

from pydantic_core import PydanticUndefined
from sqlalchemy import Column, Date, Float, Integer, MetaData, Table, Text

from auto_rest.interfaces import create_interface


class TestCreateInterface(unittest.TestCase):
    """Unit tests for the `create_interface` method."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create a dummy database table to generate interfaces from.

        Table is designed with columns having a mix of types, defaults, and nullability.
        """

        cls.table = Table(
            "test_model", MetaData(),
            Column("id1", Integer, primary_key=True),
            Column("id2", Integer, primary_key=True),
            Column("str_nul", Text, nullable=True),
            Column("str_req", Text, nullable=False),
            Column("float_nul_default", Float, default=5, nullable=True),
            Column("float_req_default", Float, default=5, nullable=False),
            Column("date_func", Date, default=date.today),
        )

    def test_field_types(self) -> None:
        """Verify the interface includes correctly typed fields for all columns."""

        interface = create_interface(self.table)

        self.assertEqual(int, interface.__annotations__["id1"])
        self.assertEqual(int, interface.__annotations__["id2"])
        self.assertEqual(str | None, interface.__annotations__["str_nul"])
        self.assertEqual(str, interface.__annotations__["str_req"])
        self.assertEqual(float | None, interface.__annotations__["float_nul_default"])
        self.assertEqual(float | None, interface.__annotations__["float_req_default"])
        self.assertEqual(date | None, interface.__annotations__["date_func"])

    def test_field_defaults(self) -> None:
        """Verify default field values match the input table."""

        interface = create_interface(self.table)

        self.assertEqual(PydanticUndefined, interface.model_fields["id1"].default)
        self.assertEqual(PydanticUndefined, interface.model_fields["id2"].default)
        self.assertEqual(None, interface.model_fields["str_nul"].default)
        self.assertEqual(PydanticUndefined, interface.model_fields["str_req"].default)
        self.assertEqual(5, interface.model_fields["float_nul_default"].default)
        self.assertEqual(5, interface.model_fields["float_req_default"].default)
        self.assertEqual(date.today(), interface.model_fields["date_func"].default(None))

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
        self.assertEqual(None, interface.model_fields["str_nul"].default)
        self.assertEqual(None, interface.model_fields["str_req"].default)
        self.assertEqual(5, interface.model_fields["float_nul_default"].default)
        self.assertEqual(5, interface.model_fields["float_req_default"].default)
        self.assertEqual(date.today(), interface.model_fields["date_func"].default(None))

    def test_pk_only_fields(self) -> None:
        """Verify the interface only includes primary key columns when `pk_only` is enabled."""

        interface = create_interface(self.table, pk_only=True)
        self.assertCountEqual(["id1", "id2"], interface.model_fields.keys())
        self.assertEqual(interface.__annotations__["id1"], int)
        self.assertEqual(interface.__annotations__["id2"], int)
