from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Column, Integer, MetaData, String, Table

from auto_rest.params import create_ordering_dependency


class TestGetOrderingParams(TestCase):
    """Unit tests for the `create_ordering_dependency` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        app = FastAPI()
        table = Table(
            "dummy_table",
            MetaData(),
            Column("id", Integer, primary_key=True),
            Column("col1", String),
        )

        @app.get("/ordering")
        def ordering(params: dict = create_ordering_dependency(table)):
            return params

        cls.client = TestClient(app)

    def test_default_params(self) -> None:
        """Verify default parameters are null."""

        response = self.client.get("/ordering")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json(), {"order_by": None, "direction": None})

    def test_valid_direction_ascending(self) -> None:
        """Verify the `asc` direction passes validation."""

        response = self.client.get("/ordering", params={"_direction_": "asc"})
        self.assertEqual({"order_by": None, "direction": "asc"}, response.json())

    def test_valid_direction_descending(self) -> None:
        """Verify the `desc` direction passes validation."""

        response = self.client.get("/ordering", params={"_direction_": "desc"})
        self.assertEqual({"order_by": None, "direction": "desc"}, response.json())

    def test_invalid_direction(self) -> None:
        """Verify invalid directions fail validation."""

        response = self.client.get("/ordering", params={"_direction_": "invalid_direction_name"})

        self.assertEqual(422, response.status_code)
        self.assertIn("Input should be 'asc' or 'desc'", str(response.json()))

    def test_case_sensitive_direction(self) -> None:
        """Verify the sort direction is case-sensitive."""

        response = self.client.get("/ordering", params={"_direction_": "DESC"})

        self.assertEqual(422, response.status_code)
        self.assertIn("Input should be 'asc' or 'desc'", str(response.json()))
