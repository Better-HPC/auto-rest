from datetime import date
from unittest import TestCase

import pydantic
from pydantic_core import PydanticUndefined
from sqlalchemy import Column, Date, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from auto_rest.models import create_db_interface

Base = declarative_base()


class DummyOrmModel(Base):
    """A dummy SQLAlchemy model used for testing."""

    __tablename__ = "test_model"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    rating = Column(Float, default=5)
    created_at = Column(Date, default=date.today)


class TestCreateDbInterface(TestCase):
    """Unit tests for the `create_db_interface` function."""

    @classmethod
    def setUp(cls) -> None:
        """Create an interface instance."""

        cls.interface = create_db_interface(DummyOrmModel)

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
