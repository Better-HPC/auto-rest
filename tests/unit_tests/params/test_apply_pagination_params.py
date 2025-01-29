from unittest import TestCase

from fastapi import Response
from sqlalchemy import Column, Integer, MetaData, Table
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import Select

from auto_rest.params import apply_pagination_params


class TestApplyPaginationParams(TestCase):
    """Unit tests for the `apply_pagination_params` function."""

    def setUp(self) -> None:
        """Create a query against a dummy database table."""

        # Dummy table to manipulate queries against
        table = Table("my_table", MetaData(), Column("id", Integer, primary_key=True))

        self.response = Response()
        self.query = select(table)

    def test_valid_params(self) -> None:
        """Verify pagination parameters are applied to the query and returned as headers."""

        params = {"limit": 10, "offset": 20}
        result_query = apply_pagination_params(self.query, params, self.response)

        # Verify the returned query is a SQLAlchemy Select object
        self.assertIsInstance(result_query, Select)

        # Verify the query contains the correct offset and limit
        self.assertEqual(10, result_query._limit)
        self.assertEqual(20, result_query._offset)

        # Verify response headers detail the provided parameters
        self.assertEqual("true", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual("10", self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual("20", self.response.headers.get("X-Pagination-Offset"))

    def test_missing_params(self) -> None:
        """Verify pagination is not applied when parameters are not provided."""

        result_query = apply_pagination_params(self.query, {}, self.response)

        self.assertEqual(None, result_query._limit)
        self.assertEqual(None, result_query._offset)

        self.assertEqual("false", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual("None", self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual("None", self.response.headers.get("X-Pagination-Offset"))

    def test_missing_limit_param(self) -> None:
        """Verify pagination is not applied when the limit parameter is not provided."""

        params = {"offset": 10}
        result_query = apply_pagination_params(self.query, params, self.response)

        self.assertEqual(None, result_query._limit)
        self.assertEqual(None, result_query._offset)

        self.assertEqual("false", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual("None", self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual("10", self.response.headers.get("X-Pagination-Offset"))

    def test_missing_offset_param(self) -> None:
        """Verify the `offset` parameter defaults to zero."""

        params = {"limit": 10}
        result_query = apply_pagination_params(self.query, params, self.response)

        self.assertEqual(10, result_query._limit)
        self.assertEqual(0, result_query._offset)

        self.assertEqual("true", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual("10", self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual("None", self.response.headers.get("X-Pagination-Offset"))

    def test_zero_limit_param(self) -> None:
        """Verify pagination is not applied when the limit parameter is zero."""

        params = {"limit": 0, "offset": 20}
        result_query = apply_pagination_params(self.query, params, self.response)

        self.assertEqual(None, result_query._limit)
        self.assertEqual(None, result_query._offset)

        self.assertEqual("false", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual("0", self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual("20", self.response.headers.get("X-Pagination-Offset"))

    def test_zero_offset_param(self) -> None:
        """Verify pagination is applied for an offset of zero."""

        params = {"limit": 10, "offset": 0}
        result_query = apply_pagination_params(self.query, params, self.response)

        self.assertEqual(10, result_query._limit)
        self.assertEqual(0, result_query._offset)

        self.assertEqual("true", self.response.headers.get("X-Pagination-Applied"))
        self.assertEqual("10", self.response.headers.get("X-Pagination-Limit"))
        self.assertEqual("0", self.response.headers.get("X-Pagination-Offset"))
