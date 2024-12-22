import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from auto_rest.handlers import welcome_handler


class TestWelcomeHandler(unittest.TestCase):
    """Unit tests for the `welcome_handler` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        app = FastAPI()
        app.add_api_route("/", welcome_handler)
        cls.client = TestClient(app)

    def test_welcome_handler(self) -> None:
        """Test the welcome handler returns the correct JSON message."""

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual({"message": "Welcome to AutoRest!"}, response.json())
