from unittest import TestCase

from sqlalchemy import Column, Integer, MetaData, Table
from sqlalchemy.sql import select

from auto_rest.queries import apply_pagination_params


class TestApplyPaginationParams(TestCase):
    """Unit tests for the `apply_pagination_params` function."""

    def setUp(self) -> None:
        """Create a query against a dummy database table."""

        # Dummy table to manipulate queries against
        table = Table("my_table", MetaData(), Column("id", Integer, primary_key=True))
        self.query = select(table)

    def test_valid_params(self) -> None:
        """Verify pagination parameters are applied to the query."""

        result_query = apply_pagination_params(self.query, limit=10, offset=20)
        self.assertEqual(10, result_query._limit)
        self.assertEqual(20, result_query._offset)

    def test_missing_params(self) -> None:
        """Verify pagination is not applied when parameters are not provided."""

        result_query = apply_pagination_params(self.query)
        self.assertEqual(None, result_query._limit)
        self.assertEqual(None, result_query._offset)

    def test_missing_limit_param(self) -> None:
        """Verify pagination is not applied when the limit parameter is not provided."""

        result_query = apply_pagination_params(self.query, offset=10)
        self.assertEqual(None, result_query._limit)
        self.assertEqual(None, result_query._offset)

    def test_missing_offset_param(self) -> None:
        """Verify the `offset` parameter defaults to zero."""

        result_query = apply_pagination_params(self.query, limit=10)
        self.assertEqual(10, result_query._limit)
        self.assertEqual(0, result_query._offset)

    def test_zero_limit_param(self) -> None:
        """Verify pagination is not applied when the limit parameter is zero."""

        result_query = apply_pagination_params(self.query, limit=0, offset=20)
        self.assertEqual(None, result_query._limit)
        self.assertEqual(None, result_query._offset)

    def test_zero_offset_param(self) -> None:
        """Verify pagination is applied for an offset of zero."""

        result_query = apply_pagination_params(self.query, limit=10, offset=0)
        self.assertEqual(10, result_query._limit)
        self.assertEqual(0, result_query._offset)
