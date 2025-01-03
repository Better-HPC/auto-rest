from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

from auto_rest.handlers import version_handler
from auto_rest.dist import version


class TestWelcomeHandler(TestCase):
    """Unit tests for the `version_handler` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        app = FastAPI()
        app.add_api_route("/", version_handler)
        cls.client = TestClient(app)

    def test_version_handler(self) -> None:
        """Test the version handler returns the correct version number."""

        response = self.client.get("/")
        self.assertEqual(200, response.status_code)
        self.assertEqual({"version": version}, response.json())
