import unittest
from unittest.mock import AsyncMock, MagicMock, PropertyMock

from sqlalchemy.engine import Engine

from auto_rest.handlers import create_meta_handler


class TestCreateMetaHandler(unittest.TestCase):
    """Unit tests for the create_meta_handler function."""

    def setUp(self):
        """Set up common test fixtures."""

        self.mock_conn_pool = MagicMock(spec=Engine)
        type(self.mock_conn_pool).dialect = PropertyMock()
        self.mock_conn_pool.dialect.name = "postgresql"
        self.mock_conn_pool.dialect.driver = "psycopg2"

        type(self.mock_conn_pool).url = PropertyMock()
        self.mock_conn_pool.url.database = "test_db"
        self.mock_conn_pool.url.host = "localhost"
        self.mock_conn_pool.url.port = 5432
        self.mock_conn_pool.url.username = "test_user"

    def test_meta_handler_returns_correct_metadata(self):
        """Test that the meta_handler function returns the correct metadata."""

        meta_handler = create_meta_handler(self.mock_conn_pool)
        self.assertTrue(callable(meta_handler), "meta_handler should be callable.")

        async def async_test():
            metadata = await meta_handler()
            self.assertEqual(metadata["dialect"], "postgresql")
            self.assertEqual(metadata["driver"], "psycopg2")
            self.assertEqual(metadata["database"], "test_db")
            self.assertEqual(metadata["host"], "localhost")
            self.assertEqual(metadata["port"], 5432)
            self.assertEqual(metadata["username"], "test_user")

        AsyncMock.run_until_complete(async_test())
