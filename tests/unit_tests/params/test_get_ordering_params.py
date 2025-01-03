from unittest import TestCase

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from auto_rest.params import get_ordering_params


class TestGetOrderingParams(TestCase):
    """Unit tests for the `get_ordering_params` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        app = FastAPI()

        @app.get("/ordering")
        def ordering(params: dict = Depends(get_ordering_params)):
            return params

        cls.client = TestClient(app)

    def test_default_params(self) -> None:
        """Test default parameter values."""

        response = self.client.get("/ordering")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json(), {"order_by": None, "direction": "asc"})

    def test_valid_params(self) -> None:
        """Test valid custom parameter values."""

        response = self.client.get("/ordering", params={"_order_by_": "name", "_direction_": "desc"})
        self.assertEqual(200, response.status_code)
        self.assertEqual({"order_by": "name", "direction": "desc"}, response.json())

    def test_empty_order_by_field(self) -> None:
        """Test an empty `order_by` field is handled properly."""

        response = self.client.get("/ordering", params={"_order_by_": ""})
        self.assertEqual(200, response.status_code)
        self.assertEqual({"order_by": "", "direction": "asc"}, response.json())

    def test_case_sensitive_sort_direction(self) -> None:
        """Test case sensitivity for the sort direction input."""

        response = self.client.get("/ordering", params={"_order_by_": "created_at", "_direction_": "DESC"})
        self.assertEqual(422, response.status_code)
        self.assertIn("Input should be 'asc' or 'desc'", str(response.json()))

    def test_invalid_sort_direction(self) -> None:
        """Test an invalid sort direction fails validation."""

        response = self.client.get("/ordering", params={"_order_by_": "id", "_direction_": "invalid"})
        self.assertEqual(422, response.status_code)
        self.assertIn("Input should be 'asc' or 'desc'", str(response.json()))
