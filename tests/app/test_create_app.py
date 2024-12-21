import unittest
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import URL, Engine

from auto_rest.app import create_app
from auto_rest.metadata import NAME


class TestCreateApp(unittest.TestCase):
    """Unit tests for the `create_app` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up shared resources for test cases."""

        cls.mock_engine = MagicMock(spec=Engine)
        cls.mock_engine.url = MagicMock(spec=URL)
        cls.mock_models = {
            "user": MagicMock(),
            "post": MagicMock()
        }
        cls.app: FastAPI = create_app(cls.mock_engine, cls.mock_models)
        cls.client = TestClient(cls.app)

    def test_app_title(self) -> None:
        """Test the application's title."""

        self.assertEqual(NAME.title(), self.app.title)

    def test_root_handler(self) -> None:
        """Test the application has a root handler."""

        response = self.client.get("/")
        self.assertEqual(200, response.status_code)

    def test_version_handler(self) -> None:
        """Test the application has a version endpoint handler."""

        response = self.client.get("/version")
        self.assertEqual(200, response.status_code)

    def test_dynamic_routes(self) -> None:
        """Test dynamically created routes exist for each model."""

        for model_name in self.mock_models:
            route_path = f"/db/{model_name}/"
            route_exists = any(route.path == route_path for route in self.app.routes)
            self.assertTrue(route_exists, f"Route {route_path} does not exist.")

    def test_invalid_route(self) -> None:
        """Test accessing an invalid route."""

        response = self.client.get("/invalid")
        self.assertEqual(404, response.status_code)
        self.assertIn("Not Found", response.json()["detail"])
