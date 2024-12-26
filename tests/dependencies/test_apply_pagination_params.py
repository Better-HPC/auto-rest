from unittest import TestCase

from fastapi import Response

from auto_rest.dependencies import apply_pagination_params


class TestApplyPaginationParams(TestCase):
    """Unit tests for the `apply_pagination_params` function."""

    def test_full_list_returned_when_page_is_zero(self):
        """Test that all items are returned when the page number is zero."""

        items = [1, 2, 3, 4, 5]
        pagination = {"page": 0, "per_page": 2}
        response = Response()

        result = apply_pagination_params(items, pagination, response)

        self.assertEqual(items, result)
        self.assertEqual({'content-length': '0'}, dict(response.headers))

    def test_pagination_with_valid_page_and_per_page(self):
        """Test pagination returns the correct slice of items and sets headers."""

        items = [1, 2, 3, 4, 5]
        pagination = {"page": 2, "per_page": 2}
        response = Response()

        result = apply_pagination_params(items, pagination, response)

        self.assertEqual([3, 4], result)
        self.assertEqual(response.headers["x-total-count"], "5")
        self.assertEqual(response.headers["x-page"], "2")
        self.assertEqual(response.headers["x-per-page"], "2")
        self.assertEqual(response.headers["x-total-pages"], "3")

    def test_pagination_with_last_page(self):
        """Test pagination when the last page contains fewer items."""

        items = [1, 2, 3, 4, 5]
        pagination = {"page": 3, "per_page": 2}
        response = Response()

        result = apply_pagination_params(items, pagination, response)

        self.assertEqual([5], result)
        self.assertEqual(response.headers["x-total-count"], "5")
        self.assertEqual(response.headers["x-page"], "3")
        self.assertEqual(response.headers["x-per-page"], "2")
        self.assertEqual(response.headers["x-total-pages"], "3")

    def test_pagination_with_empty_list(self):
        """Test pagination with an empty list of items."""

        items = []
        pagination = {"page": 1, "per_page": 2}
        response = Response()

        result = apply_pagination_params(items, pagination, response)

        self.assertEqual([], result)
        self.assertEqual(response.headers["x-total-count"], "0")
        self.assertEqual(response.headers["x-page"], "1")
        self.assertEqual(response.headers["x-per-page"], "2")
        self.assertEqual(response.headers["x-total-pages"], "0")

    def test_negative_page_number(self):
        """Test behavior when the page number is negative."""

        items = [1, 2, 3, 4, 5]
        pagination = {"page": -1, "per_page": 2}
        response = Response()

        result = apply_pagination_params(items, pagination, response)

        self.assertEqual([5], result)
        self.assertEqual(response.headers["x-total-count"], "5")
        self.assertEqual(response.headers["x-page"], "-1")
        self.assertEqual(response.headers["x-per-page"], "2")
        self.assertEqual(response.headers["x-total-pages"], "3")

    def test_invalid_per_page_value(self):
        """Test an error is raised for invalid `per_page` values (zero or negative)."""

        with self.assertRaises(ValueError):
            apply_pagination_params([1, 2, 3, 4, 5], {"page": 1, "per_page": 0}, Response())

        with self.assertRaises(ValueError):
            apply_pagination_params([1, 2, 3, 4, 5], {"page": 1, "per_page": -1}, Response())
