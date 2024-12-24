import tempfile
from unittest import TestCase

from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from auto_rest.models import create_db_engine


class TestCreateDbEngine(TestCase):
    """Unit tests for the `create_db_engine` method."""

    def setUp(self) -> None:
        """Set up a temporary SQLite database file for testing."""

        self.temp_file = tempfile.NamedTemporaryFile(suffix='.db')

    def tearDown(self) -> None:
        """Clean up the temporary database file after tests."""

        self.temp_file.close()

    def test_create_sync_engine(self) -> None:
        """Test creating an engine with a synchronous driver."""

        engine = create_db_engine(f"sqlite:///{self.temp_file.name}")
        self.assertIsInstance(engine, Engine)

    def test_create_async_cengine(self) -> None:
        """Test creating an engine with an asynchronous driver."""

        engine = create_db_engine(f"sqlite+aiosqlite:///{self.temp_file.name}")
        self.assertIsInstance(engine, AsyncEngine)

    def test_invalid_url(self) -> None:
        """Test handling for an invalid database URL."""

        with self.assertRaises(Exception):
            create_db_engine("invalid_url", pool_size=5, max_overflow=10, pool_timeout=30)
