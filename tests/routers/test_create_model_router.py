from unittest import TestCase
from unittest.mock import MagicMock

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from auto_rest.routers import create_model_router

Base = declarative_base()


class SinglePKModel(Base):
    """Database model for a mock table with a single primary key."""

    __tablename__ = "single_pk_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class MultiplePKModel(Base):
    """Database model for a mock table with multiple primary key."""

    __tablename__ = "multiple_pk_model"

    id1 = Column(Integer, primary_key=True)
    id2 = Column(Integer, primary_key=True)
    name = Column(String)


class TestCreateModelRouter(TestCase):
    """Unit tests for the `create_model_router` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create a mock SQLAlchemy engine."""

        cls.mock_engine = MagicMock()

    def test_read_only_router(self) -> None:
        """Verify read-only routers only support HTTP GET operations."""

        router = create_model_router(self.mock_engine, SinglePKModel, writeable=False)
        routes = [(route.path, method) for route in router.routes for method in route.methods]

        expected_routes = [("/", "GET"), ("/{id}/", "GET"), ]
        self.assertCountEqual(expected_routes, routes)

    def test_writable_router(self) -> None:
        """Verify writable routers support all common HTTP operations."""

        router = create_model_router(self.mock_engine, SinglePKModel, writeable=True)
        routes = [(route.path, method) for route in router.routes for method in route.methods]
        expected_routes = [
            ("/", "GET"),
            ("/", "POST"),
            ("/{id}/", "GET"),
            ("/{id}/", "PUT"),
            ("/{id}/", "PATCH"),
            ("/{id}/", "DELETE"),
        ]

        self.assertCountEqual(expected_routes, routes)

    def test_multiple_primary_keys(self) -> None:
        """Verify router paths include path parameters for tables with a multiple primary keys."""

        router = create_model_router(self.mock_engine, MultiplePKModel, writeable=True)
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
