import unittest

from fastapi.middleware.cors import CORSMiddleware

from auto_rest.app import create_app


class TestCORSSettings(unittest.TestCase):
    """Unit tests for the `create_app` method."""

    def setUp(self) -> None:
        """Create a new application instance for every test."""

        self.app = create_app("TestApp", "1.0", enable_docs=True)

    def test_cors_policy(self) -> None:
        """Verify the application CORS policy allows requests from any origin."""

        cors_middleware = next(
            middleware for middleware in self.app.user_middleware if middleware.cls is CORSMiddleware
        )

        cors_settings = cors_middleware.kwargs
        self.assertEqual(cors_settings["allow_origins"], ["*"])
        self.assertTrue(cors_settings["allow_credentials"])
        self.assertTrue(cors_settings["allow_methods"], ["*"])
        self.assertTrue(cors_settings["allow_headers"], ["*"])
