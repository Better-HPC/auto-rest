from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auto_rest.queries import delete_session_record


class TestDeleteSessionRecord(IsolatedAsyncioTestCase):
    """Unit tests for the `delete_session_record` function."""

    @staticmethod
    async def _test_session_deletion(session_type: type[Session] | type[AsyncSession]) -> None:
        """Helper method to test a session object calls the `delete` method.

        Args:
            session_type: The session type to be tested.
        """

        mock_session = MagicMock(spec=session_type)
        record = MagicMock()

        await delete_session_record(mock_session, record)
        mock_session.delete.assert_called_once_with(record)

    async def test_delete_sync_session(self) -> None:
        """Test deleting a record with a synchronous session."""

        await self._test_session_deletion(Session)

    async def test_delete_async_session(self) -> None:
        """Test deleting a record with an asynchronous session."""

        await self._test_session_deletion(AsyncSession)
