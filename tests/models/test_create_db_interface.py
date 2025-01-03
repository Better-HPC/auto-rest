import unittest
from datetime import date

import pydantic
from sqlalchemy import Column, Date, Float, Integer, String

from auto_rest.models import create_db_interface, ModelBase


class DummyOrmModel(ModelBase):
    """A dummy SQLAlchemy model used for testing."""

    __tablename__ = "test_model"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    rating = Column(Float, default=5)
    created_at = Column(Date, default=date.today)


class TestCreateDbInterface(unittest.TestCase):
    """Unit tests for the `create_db_interface` function."""

    @classmethod
    def setUp(cls) -> None:
        """Create an interface instance."""

        cls.interface = create_db_interface(DummyOrmModel)

    def test_interface_fields(self) -> None:
        """Test the generated Pydantic model has the correct fields."""

        self.assertTrue(issubclass(self.interface, pydantic.BaseModel))
        self.assertCountEqual(["id", "title", "rating", "created_at"], self.interface.__annotations__)

    def test_field_types(self) -> None:
        """Test interface fields have the correct type annotations."""

        self.assertEqual(self.interface.__annotations__["id"], int)
        self.assertEqual(self.interface.__annotations__["title"], str)
        self.assertEqual(self.interface.__annotations__["rating"], float)
        self.assertEqual(self.interface.__annotations__["created_at"], date)

    def test_field_defaults(self) -> None:
        """Test interface fields have the correct default values."""

        self.assertIsNone(self.interface.__fields__["id"].default)
        self.assertIsNone(self.interface.__fields__["title"].default)
        self.assertEqual(self.interface.__fields__["rating"].default.arg, 5)

        default_created_at = self.interface.__fields__["created_at"].default.arg
        self.assertTrue(callable(default_created_at))
        self.assertEqual(date.today(), default_created_at(None))
