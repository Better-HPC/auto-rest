from unittest import TestCase

from fastapi import Response
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import Select

from auto_rest.utils import apply_pagination_params


class TestApplyPaginationParams(TestCase):
    """Unit tests for the `apply_pagination_params` function."""

    def setUp(self) -> None:
        """Set up test structures."""

        self.response = Response()
        self.query = select()

    def test_valid_params(self) -> None:
        """Test pagination parameters are applied correctly."""

        params = {"limit": 10, "offset": 20}
        result_query = apply_pagination_params(self.query, params, self.response)

        # Check the returned query is a SQLAlchemy Select object
        self.assertIsInstance(result_query, Select)

        # Validate the query contains the correct offset and limit
        self.assertEqual(10, result_query._limit)
        self.assertEqual(20, result_query._offset)

        # Validate response headers
        self.assertEqual("true", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual("10", self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual("20", self.response.headers.get("X-Pagination-Offset"))

    def test_missing_params(self) -> None:
        """Test pagination is not applied when parameters are not provided."""

        result_query = apply_pagination_params(self.query, {}, self.response)

        self.assertEqual(None, result_query._limit)
        self.assertEqual(None, result_query._offset)

        self.assertEqual("false", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual(None, self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual(None, self.response.headers.get("X-Pagination-Offset"))

    def test_missing_limit_param(self) -> None:
        """Test pagination is not applied when the `limit` parameter is not provided."""

        params = {"offset": 10}
        result_query = apply_pagination_params(self.query, params, self.response)

        self.assertEqual(None, result_query._limit)
        self.assertEqual(None, result_query._offset)

        self.assertEqual("false", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual(None, self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual(None, self.response.headers.get("X-Pagination-Offset"))

    def test_zero_limit_param(self) -> None:
        """Test pagination is not applied when the `limit` parameter is zero."""

        params = {"limit": 0, "offset": 20}
        result_query = apply_pagination_params(self.query, params, self.response)

        self.assertEqual(None, result_query._limit)
        self.assertEqual(None, result_query._offset)

        self.assertEqual("false", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual(None, self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual(None, self.response.headers.get("X-Pagination-Offset"))

    def test_negative_limit_param(self) -> None:
        """Test a `ValueError` is raised for a negative pagination limit."""

        params = {"limit": -5, "offset": 20}
        with self.assertRaises(ValueError):
            apply_pagination_params(self.query, params, self.response)

    def test_missing_offset_param(self) -> None:
        """Test the `offset` parameter defaults to zero."""

        params = {"limit": 10}
        result_query = apply_pagination_params(self.query, params, self.response)

        self.assertEqual(10, result_query._limit)
        self.assertEqual(0, result_query._offset)

        self.assertEqual("true", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual("10", self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual("0", self.response.headers.get("X-Pagination-Offset"))

    def test_zero_offset_param(self) -> None:
        """Test setting a pagination offset of zero."""

        params = {"limit": 10, "offset": 0}
        result_query = apply_pagination_params(self.query, params, self.response)

        self.assertEqual(10, result_query._limit)
        self.assertEqual(0, result_query._offset)

        self.assertEqual("true", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual("10", self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual("0", self.response.headers.get("X-Pagination-Offset"))

    def test_negative_offset_param(self) -> None:
        """Test a `ValueError` is raised for a negative pagination offset."""

        params = {"limit": 10, "offset": -10}
        with self.assertRaises(ValueError):
            apply_pagination_params(self.query, params, self.response)
