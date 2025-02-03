from unittest import TestCase

from sqlalchemy import Column, Integer, MetaData, Table
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import asc, desc, Select

from auto_rest.queries import apply_ordering_params


class TestApplyOrderingParams(TestCase):
    """Unit tests for the `apply_ordering_params` function."""

    def setUp(self) -> None:
        """Create a query against a dummy database table."""

        # Dummy table to manipulate queries against
        table = Table("my_table", MetaData(), Column("id", Integer, primary_key=True))
        self.query = select(table)

    def test_valid_params_ascending(self) -> None:
        """Verify ascending ordering is applied to the query."""

        result_query = apply_ordering_params(self.query, order_by="id", direction="asc")
        self.assertIsInstance(result_query, Select)

        order_clause = result_query._order_by_clauses[0]
        self.assertEqual(str(asc("id")), str(order_clause))

    def test_valid_params_descending(self) -> None:
        """Verify descending ordering is applied to the query."""

        result_query = apply_ordering_params(self.query, order_by="id", direction="desc")
        self.assertIsInstance(result_query, Select)

        order_clause = result_query._order_by_clauses[0]
        self.assertEqual(str(desc("id")), str(order_clause))

    def test_missing_params(self) -> None:
        """Verify ordering is not applied when parameters are not provided."""

        result_query = apply_ordering_params(self.query)
        self.assertFalse(result_query._order_by_clauses)

    def test_missing_order_by_param(self) -> None:
        """Verify ordering is not applied when the `order_by` parameter is not provided."""

        result_query = apply_ordering_params(self.query, direction="desc")
        self.assertFalse(result_query._order_by_clauses)

    def test_missing_direction_param(self) -> None:
        """Verify the direction parameter defaults to ascending order."""

        result_query = apply_ordering_params(self.query, order_by="id")
        order_clause = result_query._order_by_clauses[0]
        self.assertEqual(str(asc("id")), str(order_clause))
