from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Column, create_engine, INTEGER
from sqlalchemy.orm import declarative_base

from auto_rest.app import create_app
from auto_rest.dist import version

Base = declarative_base()


class MockTestTable1(Base):
    """ORM model for a mock table called `test_table1`."""

    __tablename__ = "test_table1"
    col1 = Column(INTEGER, primary_key=True)


class MockTestTable2(Base):
    """ORM model for a mock table called `test_table2`."""

    __tablename__ = "test_table2"
    col2 = Column(INTEGER, primary_key=True)


class TestCreateApp(TestCase):
    """Unit tests for the `create_app` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a temporary SQLite database."""

        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=cls.engine)

        cls.mock_models = {
            "test_table1": MockTestTable1,
            "test_table2": MockTestTable2,
        }

        # Create a new FastAPI app using default options
        cls.app: FastAPI = create_app(cls.engine, cls.mock_models)
        cls.client = TestClient(cls.app)

    def test_app_metadata(self) -> None:
        """Test the application's metadata attributes."""

        self.assertEqual("Auto-REST", self.app.title)
        self.assertEqual(version, self.app.version)

    def test_has_root_endpoint(self) -> None:
        """Test the application has a root endpoint."""

        response = self.client.get("/")
        self.assertEqual(200, response.status_code)

    def test_has_version_endpoint(self) -> None:
        """Test the application has a version endpoint."""

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

    def test_has_dynamic_routes(self) -> None:
        """Test dynamically created routes exist for each model."""

        for model_name in self.mock_models:
            route_path = f"/db/{model_name}/"
            route_exists = any(route.path == route_path for route in self.app.routes)
            self.assertTrue(route_exists, f"Route {route_path} does not exist.")

    def test_invalid_route_494(self) -> None:
        """Test accessing an invalid route returns a 404."""

        response = self.client.get("/invalid")
        self.assertEqual(404, response.status_code)
        self.assertIn("Not Found", response.json()["detail"])
