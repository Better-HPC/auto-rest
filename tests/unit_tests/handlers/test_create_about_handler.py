from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

from auto_rest.handlers import create_about_handler


class TestCreateAboutHandler(TestCase):
    """Unit tests for the `create_about_handler` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a FastAPI app and test client."""

        cls.name = "FooBar"
        cls.version = "x.y.z"

        app = FastAPI()
        app.add_api_route("/", create_about_handler(cls.name, cls.version))
        cls.client = TestClient(app)

    def test_version_handler(self) -> None:
        """Verify the handler returns a 200 status and version number."""

        response = self.client.get("/")
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json(), {"name": self.name, "version": self.version})
