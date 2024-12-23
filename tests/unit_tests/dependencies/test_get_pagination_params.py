import unittest

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from auto_rest.dependencies import get_pagination_params


class TestGetPaginationParams(unittest.TestCase):
    """Unit tests for `get_pagination_params` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        app = FastAPI()

        @app.get("/pagination")
        def pagination(params: dict = Depends(get_pagination_params)):
            return params

        cls.client = TestClient(app)

    def test_default_pagination(self) -> None:
        """Test default values for pagination parameters."""

        response = self.client.get("/pagination")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"page": 0, "per_page": 10})

    def test_valid_pagination(self) -> None:
        """Test valid custom pagination values."""

        response = self.client.get("/pagination", params={"_page_": 2, "_per_page_": 20})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"page": 2, "per_page": 20})

    def test_negative_page_number(self) -> None:
        """Test negative page value passes validation."""

        response = self.client.get("/pagination", params={"_page_": -1, "_per_page_": 10})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"page": -1, "per_page": 10})

    def test_invalid_zero_per_page(self) -> None:
        """Test per_page value of 0 fails validation."""

        response = self.client.get("/pagination", params={"_page_": 0, "_per_page_": 0})
        self.assertEqual(response.status_code, 422)
        self.assertIn("Input should be greater than 0", str(response.json()))
