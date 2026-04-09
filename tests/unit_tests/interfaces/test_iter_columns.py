from unittest import TestCase

from sqlalchemy import Column, Float, Integer, MetaData, String, Table

from auto_rest.interfaces import iter_columns


class TestIterColumns(TestCase):
    """Unit tests for the `iter_columns` method."""

    def setUp(self) -> None:
        """Create a dummy SQLAlchemy table for testing."""

        self.test_table = Table(
            "test_table",
            MetaData(),
            Column("id1", Integer, primary_key=True),
            Column("id2", Integer, primary_key=True),
            Column("col1", String, nullable=True),
            Column("col2", Float, nullable=False),
        )

    def test_pk_only(self) -> None:
        """Verify only primary key columns are returned when `pk_only` is True."""

        pk_columns = [
            self.test_table.columns["id1"],
            self.test_table.columns["id2"],
        ]

        returned_columns = list(iter_columns(self.test_table, pk_only=True))
        self.assertCountEqual(pk_columns, returned_columns)

    def test_all_columns(self) -> None:
        """Verify all columns are returned by default."""

        all_columns = [
            self.test_table.columns["id1"],
            self.test_table.columns["id2"],
            self.test_table.columns["col1"],
            self.test_table.columns["col2"],
        ]

        returned_columns = list(iter_columns(self.test_table))
        self.assertCountEqual(all_columns, returned_columns)
