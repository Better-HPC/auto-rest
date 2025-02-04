from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auto_rest.queries import commit_session


class TestCommitSession(IsolatedAsyncioTestCase):
    """Unit tests for the `commit_session` function."""

    @staticmethod
    async def _test_session_commit(session_type: type[Session] | type[AsyncSession]) -> None:
        """Helper method to test a session object calls the `commit` method.

        Args:
            session_type: The session type to be tested.
        """

        mock_session = MagicMock(spec=session_type)
        await commit_session(mock_session)
        mock_session.commit.assert_called_once()

    async def test_commit_sync_session(self) -> None:
        """Verify records are committed with a synchronous session."""

        await self._test_session_commit(Session)

    async def test_commit_async_session(self) -> None:
        """Verify records are committed with an asynchronous session."""

        await self._test_session_commit(AsyncSession)
