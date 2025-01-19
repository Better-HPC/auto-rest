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

    def test_valid_directions(self) -> None:

        response = self.client.get("/ordering", params={"_direction_": "asc"})
        self.assertEqual({"order_by": None, "direction": "asc"}, response.json())

        response = self.client.get("/ordering", params={"_direction_": "desc"})
        self.assertEqual({"order_by": None, "direction": "desc"}, response.json())

    def test_invalid_direction(self) -> None:

        response = self.client.get("/ordering", params={"_direction_": "invalid_direction_name"})

        self.assertEqual(422, response.status_code)
        self.assertIn("Input should be 'asc' or 'desc'", str(response.json()))

    def test_case_sensitive_direction(self) -> None:
        """Test case sensitivity for the sort direction input."""

        response = self.client.get("/ordering", params={"_direction_": "DESC"})

        self.assertEqual(422, response.status_code)
        self.assertIn("Input should be 'asc' or 'desc'", str(response.json()))
