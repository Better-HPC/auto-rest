import unittest

from sqlalchemy import create_engine, MetaData

from auto_rest.models import create_db_metadata


class TestCreateDbMetadata(unittest.TestCase):
    """Unit tests for the `create_db_metadata` function."""

    def test_synchronous_metadata(self) -> None:
        """Test metadata mapping with a synchronous engine."""

        sync_engine = create_engine("sqlite:///:memory:")
        metadata = create_db_metadata(sync_engine)
        self.assertIsInstance(metadata, MetaData)
        self.assertEqual(len(metadata.tables), 0)

    def test_asynchronous_metadata(self) -> None:
        """Test metadata mapping with an asynchronous engine."""

        async_engine = create_engine("sqlite:///:memory:")
        metadata = create_db_metadata(async_engine)
        self.assertIsInstance(metadata, MetaData)
        self.assertEqual(len(metadata.tables), 0)
