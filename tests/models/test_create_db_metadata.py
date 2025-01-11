import asyncio
from unittest import TestCase

from sqlalchemy import Column, create_engine, INTEGER, MetaData, Table
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from auto_rest.models import create_db_metadata, DBEngine


class TestCreateDbMetadata(TestCase):
    """Unit tests for the `create_db_metadata` function."""

    @staticmethod
    def add_tables(engine: DBEngine) -> None:
        """Helper method to add test tables to the database engine.

        Args:
            engine: The SQLAlchemy engine (synchronous or asynchronous).
        """

        metadata = MetaData()
        Table("test_table1", metadata, Column("col1", INTEGER))
        Table("test_table2", metadata, Column("col2", INTEGER))

        if isinstance(engine, AsyncEngine):
            # Use run_sync to execute synchronous metadata creation
            async def create_tables():
                async with engine.begin() as conn:
                    await conn.run_sync(metadata.create_all)

            asyncio.run(create_tables())

        else:
            metadata.create_all(engine)

    def test_synchronous_metadata(self) -> None:
        """Test metadata mapping with a synchronous engine."""

        engine = create_engine("sqlite:///:memory:")
        self.add_tables(engine)

        metadata = create_db_metadata(engine)
        self.assertIsInstance(metadata, MetaData)
        self.assertEqual(2, len(metadata.tables))

        engine.dispose()

    def test_synchronous_metadata_empty_database(self) -> None:
        """Test metadata mapping with a synchronous engine against an empty database."""

        engine = create_engine("sqlite:///:memory:")

        metadata = create_db_metadata(engine)
        self.assertIsInstance(metadata, MetaData)
        self.assertEqual(0, len(metadata.tables))

        engine.dispose()

    def test_asynchronous_metadata(self) -> None:
        """Test metadata mapping with an asynchronous engine."""

        async_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.add_tables(async_engine)

        metadata = create_db_metadata(async_engine)
        self.assertIsInstance(metadata, MetaData)
        self.assertEqual(2, len(metadata.tables))

        asyncio.run(async_engine.dispose())

    def test_asynchronous_metadata_empty_database(self) -> None:
        """Test metadata mapping with an asynchronous engine against an empty database."""

        async_engine = create_async_engine("sqlite+aiosqlite:///:memory:")

        metadata = create_db_metadata(async_engine)
        self.assertIsInstance(metadata, MetaData)
        self.assertEqual(0, len(metadata.tables))

        asyncio.run(async_engine.dispose())
