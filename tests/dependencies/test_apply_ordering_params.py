from unittest import TestCase
from unittest.mock import Mock

from fastapi import Response
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import asc, desc, Select

from auto_rest.dependencies import apply_ordering_params


class TestApplyOrderingParams(TestCase):
    """Unit tests for the `apply_ordering_params` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up common test variables."""

        cls.response = Mock(spec=Response)
        cls.query = select()

    def test_valid_params_ascending(self) -> None:
        """Test parameters are applied correctly for ascending order."""

        params = {"order_by": "column_name", "direction": "asc"}
        result_query = apply_ordering_params(self.query, params, self.response)
        self.assertIsInstance(result_query, Select)

        order_clause = result_query._order_by_clauses[0]
        self.assertEqual(str(order_clause), str(asc("column_name")))

    def test_valid_params_descending(self) -> None:
        """Test parameters are applied correctly for descending order."""

        params = {"order_by": "column_name", "direction": "desc"}
        result_query = apply_ordering_params(self.query, params, self.response)
        self.assertIsInstance(result_query, Select)

        order_clause = result_query._order_by_clauses[0]
        self.assertEqual(str(order_clause), str(desc("column_name")))

    def test_invalid_direction_param(self) -> None:
        """Test an invalid direction defaults to ascending order."""

        params = {"order_by": "column_name", "direction": "invalid"}
        result_query = apply_ordering_params(self.query, params, self.response)
        self.assertIsInstance(result_query, Select)

        order_clause = result_query._order_by_clauses[0]
        self.assertEqual(str(order_clause), str(asc("column_name")))

    def test_no_direction_param(self) -> None:
        """Test that ascending order is applied by default when 'direction' is missing."""

        params = {"order_by": "column_name"}
        with self.assertRaises(ValueError):
            apply_ordering_params(self.query, params, self.response)

    def test_no_order_by_param(self) -> None:
        """Test that no ordering is applied when 'order_by' is missing."""

        params = {"direction": "asc"}
        with self.assertRaises(ValueError):
            apply_ordering_params(self.query, params, self.response)
