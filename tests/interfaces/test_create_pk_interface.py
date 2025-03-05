import unittest

from pydantic_core import PydanticUndefined
from sqlalchemy import Column, Integer, MetaData, Table, Text

from auto_rest.interfaces import create_pk_interface


class TestCreatePkInterface(unittest.TestCase):
    """Unit tests for the `create_pk_interface` method."""

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

        cls.interface = create_pk_interface(cls.table)

    def test_field_types(self) -> None:
        """Verify the interface includes correctly typed fields for primary key columns."""

        self.assertCountEqual(["id1", "id2"], self.interface.__annotations__.keys())
        self.assertEqual(int, self.interface.__annotations__["id1"])
        self.assertEqual(int, self.interface.__annotations__["id2"])

    def test_field_defaults(self) -> None:
        """Verify PK fields are marked as required."""

        self.assertEqual(PydanticUndefined, self.interface.model_fields["id1"].default)
        self.assertEqual(PydanticUndefined, self.interface.model_fields["id2"].default)
