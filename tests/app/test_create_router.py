import unittest
from unittest.mock import MagicMock

from sqlalchemy import Column, Integer, String

from auto_rest.app import create_router
from auto_rest.models import ModelBase


class SinglePKModel(ModelBase):
    """ORM for a mock table with a single primary key."""

    __tablename__ = "single_pk_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class MultiplePKModel(ModelBase):
    """ORM for a mock table with multiple primary key."""

    __tablename__ = "multiple_pk_model"

    id1 = Column(Integer, primary_key=True)
    id2 = Column(Integer, primary_key=True)
    name = Column(String)


class TestCreateRouter(unittest.TestCase):
    """Unit tests for the """

    @classmethod
    def setUpClass(cls) -> None:
        """Create a mock SQLAlchemy engine."""

        cls.mock_engine = MagicMock()

    def test_router_single_primary_key(self) -> None:
        """Test router create for a table with a single primary key."""

        router = create_router(self.mock_engine, SinglePKModel)
        actual_routes = [(route.path, method) for route in router.routes for method in route.methods]
        expected_routes = [
            ("/", "GET"),
            ("/", "POST"),
            ("/{id}/", "GET"),
            ("/{id}/", "PUT"),
            ("/{id}/", "PATCH"),
            ("/{id}/", "DELETE"),
        ]

        self.assertCountEqual(expected_routes, actual_routes)

    def test_router_multiple_primary_keys(self) -> None:
        """Test router create for a table with a multiple primary keys."""

        router = create_router(self.mock_engine, MultiplePKModel)
        actual_routes = [(route.path, method) for route in router.routes for method in route.methods]
        expected_routes = [
            ("/", "GET"),
            ("/", "POST"),
            ("/{id1}/{id2}/", "GET"),
            ("/{id1}/{id2}/", "PUT"),
            ("/{id1}/{id2}/", "PATCH"),
            ("/{id1}/{id2}/", "DELETE"),
        ]

        self.assertCountEqual(expected_routes, actual_routes)
