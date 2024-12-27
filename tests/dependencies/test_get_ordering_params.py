from unittest import TestCase

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from auto_rest.utils import get_ordering_params


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

    def test_default_ordering(self) -> None:
        """Test the default sorting direction when `order_by` is not provided."""

        response = self.client.get("/ordering")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"order_by": None, "direction": "asc"})

    def test_valid_ordering_params(self) -> None:
        """Test a valid `order_by` field and sort direction."""

        response = self.client.get("/ordering", params={"_order_by_": "name", "_direction_": "desc"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"order_by": "name", "direction": "desc"})

    def test_case_sensitive_sort_direction(self) -> None:
        """Test case sensitivity for the sort direction input."""

        response = self.client.get("/ordering", params={"_order_by_": "created_at", "_direction_": "DESC"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("Input should be 'asc' or 'desc'", str(response.json()))

    def test_invalid_sort_direction(self) -> None:
        """Test an invalid sort direction fails validation."""

        response = self.client.get("/ordering", params={"_order_by_": "id", "_direction_": "invalid"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("Input should be 'asc' or 'desc'", str(response.json()))

    def test_only_order_by_provided(self) -> None:
        """Test `order_by` provided without explicitly setting `direction`."""

        response = self.client.get("/ordering", params={"_order_by_": "updated_at"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"order_by": "updated_at", "direction": "asc"})

    def test_empty_order_by_field(self) -> None:
        """Test empty `order_by` field is handled properly."""

        response = self.client.get("/ordering", params={"_order_by_": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"order_by": "", "direction": "asc"})
