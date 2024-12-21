import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from auto_rest.handlers import version_handler
from auto_rest.metadata import VERSION


class TestWelcomeHandler(unittest.TestCase):
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual({"version": VERSION}, response.json())
