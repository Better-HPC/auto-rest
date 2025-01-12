from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from auto_rest.handlers import create_meta_handler


class TestCreateMetaHandler(TestCase):
    """Unit tests for the `create_meta_handler` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        # Create a database engine and define the expected metadata
        cls.engine = create_engine("sqlite:///:memory:")
        cls.meta = {'database': ':memory:',
                    'dialect': 'sqlite',
                    'driver': 'pysqlite',
                    'host': None,
                    'port': None,
                    'username': None}

        app = FastAPI()
        app.add_api_route("/", create_meta_handler(cls.engine))
        cls.client = TestClient(app)

    def test_meta_handler(self) -> None:
        """Test the meta handler returns a 200 status and database metadata."""

        response = self.client.get("/")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json(), self.meta)
