from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

from auto_rest.handlers import create_welcome_handler


class TestCreateWelcomeHandler(TestCase):
    """Unit tests for the `create_welcome_handler` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        app = FastAPI()
        app.add_api_route("/", create_welcome_handler())
        cls.client = TestClient(app)

    def test_welcome_handler(self) -> None:
        """Test the version handler returns a 200 status and welcome message."""

        response = self.client.get("/")
        self.assertEqual(200, response.status_code)
        self.assertEqual({"message": "Welcome to Auto-Rest!"}, response.json())
