from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from auto_rest.handlers import create_engine_handler


class TestCreateEngineHandler(TestCase):
    """Unit tests for the `create_engine_handler` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        # Create a database engine and define the expected configuration
        cls.engine = create_engine("sqlite:///:memory:")
        cls.config = {'database': ':memory:', 'dialect': 'sqlite', 'driver': 'pysqlite'}

        app = FastAPI()
        app.add_api_route("/", create_engine_handler(cls.engine))
        cls.client = TestClient(app)

    def test_engine_handler(self) -> None:
        """Test the engine handler returns a 200 status and the engine configuration."""

        response = self.client.get("/")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json(), self.config)
