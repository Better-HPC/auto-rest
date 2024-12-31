import tempfile
from unittest import TestCase
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from auto_rest.app import create_app
from auto_rest.dist import version


class TestCreateApp(TestCase):
    """Unit tests for the `create_app` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a temporary SQLite database."""

        # Create a temporary SQLite database
        cls.temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.engine = create_engine(f"sqlite:///{cls.temp_file.name}", echo=True)

        # Mock models for database tables
        cls.mock_models = {
            "user": MagicMock(
                __name__="User",
                __table__=MagicMock(
                    primary_key=MagicMock(
                        columns=[MagicMock(name="id")]
                    )
                )
            )
        }

        # Create a new FastAPI app using default options
        cls.app: FastAPI = create_app(cls.engine, cls.mock_models)
        cls.client = TestClient(cls.app)

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up the temporary database file."""

        cls.temp_file.close()

    def test_app_meta(self) -> None:
        """Test the application's metadata attributes."""

        self.assertEqual("Auto-REST", self.app.title)
        self.assertEqual(version, self.app.version)

    def test_root_handler(self) -> None:
        """Test the application has a root handler."""

        response = self.client.get("/")
        self.assertEqual(200, response.status_code)

    def test_version_handler(self) -> None:
        """Test the application has a version endpoint handler."""

        response = self.client.get("/version")
        self.assertEqual(200, response.status_code)

    def test_docs_endpoint_disabled(self) -> None:
        """Test the application has no `/docs` endpoint by default."""

        default_app = create_app(self.engine, self.mock_models)
        default_client = TestClient(default_app)
        response = default_client.get("/docs")
        self.assertEqual(404, response.status_code)

    def test_docs_endpoint_enabled(self) -> None:
        """Test the application has a `/docs` endpoint when enabled."""

        default_app = create_app(self.engine, self.mock_models, enable_docs=True)
        default_client = TestClient(default_app)
        response = default_client.get("/docs")
        self.assertEqual(200, response.status_code)

    def test_meta_endpoint_disabled(self) -> None:
        """Test the application has no `/meta` endpoint by default."""

        default_app = create_app(self.engine, self.mock_models)
        default_client = TestClient(default_app)
        response = default_client.get("/meta")
        self.assertEqual(404, response.status_code)

    def test_meta_endpoint_enabled(self) -> None:
        """Test the application has a `/meta` endpoint when enabled."""

        default_app = create_app(self.engine, self.mock_models, enable_meta=True)
        default_client = TestClient(default_app)
        response = default_client.get("/meta")
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
