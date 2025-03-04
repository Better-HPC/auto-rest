from unittest import TestCase

from sqlalchemy import URL
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from auto_rest.models import create_db_engine


class TestCreateDbEngine(TestCase):
    """Unit tests for the `create_db_engine` method."""

    def test_create_sync_engine(self) -> None:
        """Verify synchronous drivers return synchronous engines."""

        url = URL.create(drivername="sqlite", database=":memory:")
        engine = create_db_engine(url)

        self.assertIsInstance(engine, Engine)
        self.assertEqual("pysqlite", engine.driver)
        self.assertEqual(url, engine.url)

    def test_create_async_engine(self) -> None:
        """Verify asynchronous drivers return asynchronous engines."""

        url = URL.create(drivername="sqlite+aiosqlite", database=":memory:")
        async_engine = create_db_engine(url)

        self.assertIsInstance(async_engine, AsyncEngine)
        self.assertEqual("aiosqlite", async_engine.driver)
        self.assertEqual(url, async_engine.url)

    def test_invalid_url(self) -> None:
        """Verify invalid database URLs raise an error."""

        with self.assertRaises(Exception):
            # noinspection PyTypeChecker
            create_db_engine("invalid_url")
