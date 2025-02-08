import logging
import unittest
from unittest.mock import AsyncMock, MagicMock

from fastapi import Request, Response

from auto_rest.app import logging_middleware


class TestLoggingMiddleware(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the `logging_middleware` function."""

    def setUp(self) -> None:
        self.request = MagicMock(spec=Request)
        self.request.method = "GET"
        self.request.client = MagicMock()
        self.request.client.host = "40.30.20.10"
        self.request.url.path = "/test-path"

    async def test_logging_middleware_info(self) -> None:
        """Verify INFO level log messages are recorded."""

        call_next = AsyncMock(return_value=Response(status_code=200))
        with self.assertLogs(level=logging.INFO) as caplog:
            await logging_middleware(self.request, call_next)

        self.assertTrue(any("GET (200) 40.30.20.10 - /test-path" in message for message in caplog.output))

    async def test_logging_middleware_error(self) -> None:
        """Verify ERROR level log messages are recorded."""

        call_next = AsyncMock(return_value=Response(status_code=500))
        with self.assertLogs(level=logging.ERROR) as caplog:
            await logging_middleware(self.request, call_next)

        self.assertTrue(any("GET (500) 40.30.20.10 - /test-path" in message for message in caplog.output))
