from unittest import TestCase
from unittest.mock import Mock

from fastapi import Response
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import Select

from auto_rest.dependencies import apply_pagination_params


class TestApplyPaginationParams(TestCase):
    """Unit tests for the `apply_pagination_params` function."""

    def setUp(self) -> None:
        """Set up test structures."""

        self.response = Mock(spec=Response)  # Mocked Response object
        self.query = select()  # Example SQLAlchemy query

    def test_valid_params(self) -> None:
        """Test pagination parameters are applied correctly."""

        params = {"limit": 10, "offset": 20}
        result_query = apply_pagination_params(self.query, params, self.response)

        # Check the returned query is a SQLAlchemy Select object
        self.assertIsInstance(result_query, Select)

        # Assert the query contains the correct offset and limit
        self.assertEqual(result_query._limit, 10)
        self.assertEqual(result_query._offset, 20)

    def test_missing_params(self) -> None:
        """Test a ValueError is raised for missing parameters."""

        params = {"limit": 10}  # Missing 'offset'
        with self.assertRaises(ValueError):
            apply_pagination_params(self.query, params, self.response)

        params = {"offset": 20}  # Missing 'limit'
        with self.assertRaises(ValueError):
            apply_pagination_params(self.query, params, self.response)

    def test_invalid_params(self) -> None:
        """Test a ValueError is raise for invalid pagination values."""

        params = {"limit": -5, "offset": -10}
        with self.assertRaises(ValueError):
            apply_pagination_params(self.query, params, self.response)

    def test_zero_value_params(self) -> None:
        """Test pagination parameters with zero values."""

        params = {"limit": 0, "offset": 0}
        result_query = apply_pagination_params(self.query, params, self.response)

        # Assert the query has offset and limit set to zero
        self.assertEqual(result_query._limit, 0)
        self.assertEqual(result_query._offset, 0)
