from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auto_rest.queries import execute_session_query


class TestExecuteSessionQuery(IsolatedAsyncioTestCase):
    """Unit tests for the `execute_session_query` function."""

    @staticmethod
    async def _test_session_execution(session_type: type[Session] | type[AsyncSession]) -> None:
        """Helper method to test a session object calls the `execute` method.

        Args:
            session_type: The session type to be tested.
        """

        # Create mock objects for the session and query
        mock_session = MagicMock(spec=session_type)
        mock_query = MagicMock()
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result

        # Verify execute() was called and returns the correct result
        result = await execute_session_query(mock_session, mock_query)
        mock_session.execute.assert_called_once_with(mock_query)
        assert result == mock_result

    async def test_execute_sync_session(self) -> None:
        """Verify queries are executed with a synchronous session."""

        await self._test_session_execution(Session)

    async def test_execute_async_session(self) -> None:
        """Verify queries are executed with an asynchronous session."""

        await self._test_session_execution(AsyncSession)
