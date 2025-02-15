import logging
import unittest
from unittest.mock import AsyncMock, MagicMock

from fastapi import Request
from starlette.responses import Response

from auto_rest.app import logging_middleware


class TestLoggingMiddleware(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the `logging_middleware` function."""

    def setUp(self) -> None:
        """Create a dummy HTTP request."""

        self.request = MagicMock(spec=Request)
        self.request.method = "GET"
        self.request.client = MagicMock()
        self.request.client.host = "40.30.20.10"
        self.request.client.port = 12345
        self.request.url.path = "/test-path"

    async def test_logging_middleware_info(self) -> None:
        """Verify INFO level log messages are recorded."""

        call_next = AsyncMock(return_value=Response(status_code=200))

        with self.assertLogs("auto_rest.access", level=logging.INFO) as caplog:
            await logging_middleware(self.request, call_next)

        self.assertTrue(
            any("200 OK" in message for message in caplog.output),
            "Expected log message with '200 OK' not found in logs."
        )

    async def test_logging_middleware_error(self) -> None:
        """Verify ERROR level log messages are recorded."""

        call_next = AsyncMock(return_value=Response(status_code=500))

        with self.assertLogs("auto_rest.access", level=logging.ERROR) as caplog:
            await logging_middleware(self.request, call_next)

        self.assertTrue(
            any("500 Internal Server Error" in message for message in caplog.output),
            "Expected log message with '500 Internal Server Error' not found in logs."
        )

    async def test_logging_middleware_exception(self) -> None:
        """Verify that exceptions are logged properly and propagated."""

        call_next = AsyncMock(side_effect=ValueError("Test exception"))

        with self.assertLogs("auto_rest.access", level=logging.ERROR) as caplog:
            with self.assertRaises(ValueError):
                await logging_middleware(self.request, call_next)

        self.assertTrue(
            any("Test exception" in message for message in caplog.output),
            "Expected log message for 'Test exception' not found in logs."
        )
