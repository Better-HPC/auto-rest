from unittest import TestCase

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from auto_rest.utils import get_pagination_params


class TestGetPaginationParams(TestCase):
    """Unit tests for `get_pagination_params` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        app = FastAPI()

        @app.get("/pagination")
        def pagination(params: dict = Depends(get_pagination_params)):
            return params

        cls.client = TestClient(app)

    def test_default_params(self) -> None:
        """Test default parameter values."""

        response = self.client.get("/pagination")
        self.assertEqual(200, response.status_code)
        self.assertEqual({'limit': 10, 'offset': 0}, response.json())

    def test_valid_params(self) -> None:
        """Test valid custom parameter values."""

        response = self.client.get("/pagination", params={"_limit_": 2, "_offset_": 20})
        self.assertEqual(200, response.status_code)
        self.assertEqual({"limit": 2, "offset": 20}, response.json())

    def test_zero_limit(self) -> None:
        """Test a zero limit value passes validation."""

        response = self.client.get("/pagination", params={"_limit_": 0, "_offset_": 20})
        self.assertEqual(200, response.status_code)
        self.assertEqual({"limit": 0, "offset": 20}, response.json())

    def test_negative_limit(self) -> None:
        """Test negative limit values fail validation."""

        response = self.client.get("/pagination", params={"_limit_": -1})
        self.assertEqual(422, response.status_code)

        error_detail = response.json()['detail'][0]
        self.assertEqual("Input should be greater than or equal to 0", error_detail['msg'])

    def test_zero_offset(self) -> None:
        """Test a zero offset value passes validation."""

        response = self.client.get("/pagination", params={"_limit_": 10, "_offset_": 0})
        self.assertEqual(200, response.status_code)
        self.assertEqual({"limit": 10, "offset": 0}, response.json())

    def test_negative_offset(self) -> None:
        """Test negative offset values fail validation."""

        response = self.client.get("/pagination", params={"_offset_": -1})
        self.assertEqual(422, response.status_code)

        error_detail = response.json()['detail'][0]
        self.assertEqual("Input should be greater than or equal to 0", error_detail['msg'])

