from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

from auto_rest.handlers import create_version_handler


class TestCreateVersionHandler(TestCase):
    """Unit tests for the `create_version_handler` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        app = FastAPI()
        app.add_api_route("/", create_version_handler())
        cls.client = TestClient(app)

    def test_version_handler(self) -> None:
        """Test the version handler returns a 200 sstatus and version number."""

        response = self.client.get("/")
        self.assertEqual(200, response.status_code)
        self.assertIn("version", response.json())
