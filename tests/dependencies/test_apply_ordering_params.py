from unittest import skip, TestCase
from unittest.mock import Mock

from fastapi import Response
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import asc, desc, Select

from auto_rest.utils import apply_ordering_params


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
        self.assertEqual(str(asc("column_name")), str(order_clause))

    def test_valid_params_descending(self) -> None:
        """Test parameters are applied correctly for descending order."""

        params = {"order_by": "column_name", "direction": "desc"}
        result_query = apply_ordering_params(self.query, params, self.response)
        self.assertIsInstance(result_query, Select)

        order_clause = result_query._order_by_clauses[0]
        self.assertEqual(str(desc("column_name")), str(order_clause))

    def test_missing_params(self) -> None:
        """Test ordering is not applied when parameters are not provided."""

        result_query = apply_ordering_params(self.query, {}, self.response)
        self.assertFalse(result_query._order_by_clauses)

    def test_missing_order_by_param(self):
        """Test ordering is not applied when the `order_by` parameter is not provided."""

        params = {"direction": "desc"}
        result_query = apply_ordering_params(self.query, params, self.response)
        self.assertFalse(result_query._order_by_clauses)

    @skip("This test requires implementing additional testing structures.")
    def test_invalid_order_by_param(self):
        """Test a ValueError is raised for an invalid `order_by` parameter."""

        self.fail()

    def test_missing_direction_param(self) -> None:
        """Test the `direction` parameter defaults to ascending."""

        params = {"order_by": "column_name"}
        result_query = apply_ordering_params(self.query, params, self.response)

        order_clause = result_query._order_by_clauses[0]
        self.assertEqual(str(asc("column_name")), str(order_clause))

    def test_invalid_direction_param(self) -> None:
        """Test a ValueError is raised for an invalid `direction` parameter."""

        params = {"order_by": "column_name", "direction": "invalid"}
        with self.assertRaises(ValueError):
            apply_ordering_params(self.query, params, self.response)
