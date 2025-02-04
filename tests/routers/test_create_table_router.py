from unittest import TestCase
from unittest.mock import MagicMock

from sqlalchemy import Column, Integer, MetaData, String, Table

from auto_rest.routers import create_table_router


class TestCreateTableRouter(TestCase):
    """Unit tests for the `create_table_router` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Create a mock SQLAlchemy engine."""

        cls.mock_engine = MagicMock()
        cls.no_pk_table = Table(
            "no_pk_model",
            MetaData(),
            Column("id", Integer),
            Column("name", String),
        )

        cls.single_pk_table = Table(
            "single_pk_model",
            MetaData(),
            Column("id", Integer, primary_key=True),
            Column("name", String),
        )

        cls.multiple_pk_table = Table(
            "multiple_pk_model",
            MetaData(),
            Column("id1", Integer, primary_key=True),
            Column("id2", Integer, primary_key=True),
            Column("name", String),
        )

    def test_read_only_router(self) -> None:
        """Verify read-only routers only support HTTP GET operations."""

        router = create_table_router(self.mock_engine, self.single_pk_table, writeable=False)
        routes = [(route.path, method) for route in router.routes for method in route.methods]

        expected_routes = [("/", "GET"), ("/{id}/", "GET"), ]
        self.assertCountEqual(expected_routes, routes)

    def test_writable_router(self) -> None:
        """Verify writable routers support all common HTTP operations."""

        router = create_table_router(self.mock_engine, self.single_pk_table, writeable=True)
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
        """Verify router paths include path parameters for tables with multiple primary keys."""

        router = create_table_router(self.mock_engine, self.multiple_pk_table, writeable=True)
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

    def test_no_primary_keys(self) -> None:
        """Verify router paths do not include PK endpoints for tables with no primary keys."""

        router = create_table_router(self.mock_engine, self.no_pk_table, writeable=True)
        actual_routes = [(route.path, method) for route in router.routes for method in route.methods]
        expected_routes = [
            ("/", "GET"),
            ("/", "POST"),
        ]

        self.assertCountEqual(expected_routes, actual_routes)
