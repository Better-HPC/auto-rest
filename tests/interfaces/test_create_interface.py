import unittest
from datetime import date

from pydantic_core import PydanticUndefined
from sqlalchemy import Column, Date, Float, Integer, MetaData, Table, Text

from auto_rest.interfaces import create_interface


class TestCreateInterface(unittest.TestCase):
    """Unit tests for the `create_interface` method."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create a new Pydantic interface from a dummy Sqlalchemy table.

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

        cls.interface = create_interface(cls.table)

    def test_field_types(self) -> None:
        """Verify the interface includes correctly typed fields for all columns."""

        self.assertEqual(int, self.interface.__annotations__["id1"])
        self.assertEqual(int, self.interface.__annotations__["id2"])
        self.assertEqual(str | None, self.interface.__annotations__["str_nul"])
        self.assertEqual(str, self.interface.__annotations__["str_req"])
        self.assertEqual(float | None, self.interface.__annotations__["float_nul_default"])
        self.assertEqual(float | None, self.interface.__annotations__["float_req_default"])
        self.assertEqual(date | None, self.interface.__annotations__["date_func"])

    def test_field_defaults(self) -> None:
        """Verify default field values match the input table."""

        self.assertEqual(PydanticUndefined, self.interface.model_fields["id1"].default)
        self.assertEqual(PydanticUndefined, self.interface.model_fields["id2"].default)
        self.assertEqual(None, self.interface.model_fields["str_nul"].default)
        self.assertEqual(PydanticUndefined, self.interface.model_fields["str_req"].default)
        self.assertEqual(5, self.interface.model_fields["float_nul_default"].default)
        self.assertEqual(5, self.interface.model_fields["float_req_default"].default)
        self.assertEqual(date.today(), self.interface.model_fields["date_func"].default(None))
