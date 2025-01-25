from datetime import date
from unittest import TestCase
from unittest.mock import MagicMock

import pydantic
from pydantic_core import PydanticUndefined
from sqlalchemy import Column, Date, Float, Integer, MetaData, String, Table

from auto_rest.models import create_db_interface


class TestCreateDbInterface(TestCase):
    """Unit tests for the `create_db_interface` function."""

    @classmethod
    def setUp(cls) -> None:
        """Create an interface instance."""

        cls.table = Table(
            "test_model",
            MetaData(),
            Column("id", Integer, primary_key=True),
            Column("title", String),
            Column("rating", Float, default=5),
            Column("created_at", Date, default=date.today),
        )

        cls.interface = create_db_interface(cls.table)

    def test_interface_fields(self) -> None:
        """Verify the generated Pydantic model has the correct fields."""

        self.assertTrue(issubclass(self.interface, pydantic.BaseModel))
        self.assertCountEqual(["id", "title", "rating", "created_at"], self.interface.__annotations__)

    def test_field_types(self) -> None:
        """Verify interface fields have the correct type annotations."""

        self.assertEqual(self.interface.__annotations__["id"], int)
        self.assertEqual(self.interface.__annotations__["title"], str)
        self.assertEqual(self.interface.__annotations__["rating"], float)
        self.assertEqual(self.interface.__annotations__["created_at"], date)

    def test_field_defaults(self) -> None:
        """Verify interface fields have the correct default values."""

        # Verify fields without default values
        self.assertEqual(PydanticUndefined, self.interface.model_fields["id"].default)
        self.assertEqual(PydanticUndefined, self.interface.model_fields["title"].default)

        # Verify fields with fixed default values
        self.assertEqual(self.interface.model_fields["rating"].default.arg, 5)

        # Verify fields with dynamic default values
        default_created_at = self.interface.model_fields["created_at"].default.arg
        self.assertTrue(callable(default_created_at))
        self.assertEqual(date.today(), default_created_at(None))
