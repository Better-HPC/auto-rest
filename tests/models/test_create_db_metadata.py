from unittest import TestCase

from sqlalchemy import Column, create_engine, Engine, MetaData, Table, VARCHAR

from auto_rest.models import create_db_metadata


class TestCreateDbMetadata(TestCase):
    """Unit tests for the `create_db_metadata` function."""

    @staticmethod
    def add_tables(engine: Engine) -> None:
        """Helper method to add test tables to the database engine.

        Args:
            engine: The SQLAlchemy engine (synchronous or asynchronous).
        """

        metadata = MetaData()
        Table("test_table1", metadata, Column("col", VARCHAR(100)))
        Table("test_table2", metadata, Column("col", VARCHAR(100)))
        metadata.create_all(engine)

    def test_synchronous_metadata(self) -> None:
        """Test metadata mapping with a synchronous engine."""

        sync_engine = create_engine("sqlite:///:memory:")
        self.add_tables(sync_engine)

        metadata = create_db_metadata(sync_engine)
        self.assertIsInstance(metadata, MetaData)
        self.assertEqual(len(metadata.tables), 2)

    def test_asynchronous_metadata(self) -> None:
        """Test metadata mapping with an asynchronous engine."""

        async_engine = create_engine("sqlite:///:memory:")
        self.add_tables(async_engine)

        metadata = create_db_metadata(async_engine)
        self.assertIsInstance(metadata, MetaData)
        self.assertEqual(len(metadata.tables), 2)

    def test_empty_database_synchronous_metadata(self) -> None:
        """Test metadata mapping with a synchronous engine."""

        sync_engine = create_engine("sqlite:///:memory:")
        metadata = create_db_metadata(sync_engine)
        self.assertIsInstance(metadata, MetaData)
        self.assertEqual(len(metadata.tables), 0)

    def test_empty_database_asynchronous_metadata(self) -> None:
        """Test metadata mapping with an asynchronous engine."""

        async_engine = create_engine("sqlite:///:memory:")
        metadata = create_db_metadata(async_engine)
        self.assertIsInstance(metadata, MetaData)
        self.assertEqual(len(metadata.tables), 0)
