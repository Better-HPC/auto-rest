import tempfile
from unittest import TestCase

from sqlalchemy import URL
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

        url = URL.create(drivername="sqlite", database=self.temp_file.name)
        engine = create_db_engine(url)

        self.assertIsInstance(engine, Engine)
        self.assertEqual(url, engine.url)

    def test_create_async_cengine(self) -> None:
        """Test creating an engine with an asynchronous driver."""

        url = URL.create(drivername="sqlite+aiosqlite", database=self.temp_file.name)
        engine = create_db_engine(url)

        self.assertIsInstance(engine, AsyncEngine)
        self.assertEqual(url, engine.url)

    def test_invalid_url(self) -> None:
        """Test handling for an invalid database URL."""

        with self.assertRaises(Exception):
            create_db_engine("invalid_url")
