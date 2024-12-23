import tempfile
import unittest

from sqlalchemy.engine import Engine

from auto_rest.models import create_connection_pool


class TestCreateConnectionPool(unittest.TestCase):
    """Unit tests for the `create_connection_pool` method."""

    def setUp(self) -> None:
        """Set up a temporary SQLite database file for testing."""

        self.temp_file = tempfile.NamedTemporaryFile(suffix='.db')
        self.db_url = f"sqlite:///{self.temp_file.name}"

    def tearDown(self) -> None:
        """Clean up the temporary database file after tests."""

        self.temp_file.close()

    def test_create_connection_pool_success(self) -> None:
        """Test the successful creation of a database connection pool."""

        pool_size = 5
        max_overflow = 10
        pool_timeout = 30
        engine = create_connection_pool(self.db_url, pool_size, max_overflow, pool_timeout)

        # Check the connection parameters are correctly set
        self.assertIsInstance(engine, Engine)
        self.assertEqual(engine.pool.size(), pool_size)
        self.assertEqual(engine.pool._max_overflow, max_overflow)
        self.assertEqual(engine.pool.timeout(), pool_timeout)

    def test_invalid_url(self) -> None:
        """Test handling an invalid database URL."""

        url = "invalid_url"
        with self.assertRaises(Exception):
            create_connection_pool(url, pool_size=5, max_overflow=10, pool_timeout=30)
