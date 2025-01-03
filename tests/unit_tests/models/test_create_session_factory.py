from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session

from auto_rest.models import create_session_factory


class TestCreateDbDependency(IsolatedAsyncioTestCase):
    """Unit tests for the `create_db_dependency` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a test database engine."""

        cls.test_engine = create_engine("sqlite:///:memory:")
        cls.test_async_engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    def test_session_is_active(self) -> None:
        """Test the generated function yields an active session."""

        db_dependency = create_session_factory(self.test_engine)
        session_generator = db_dependency()

        with next(session_generator) as session:
            self.assertIsInstance(session, Session)
            self.assertTrue(session.is_active)
            self.assertIs(self.test_engine, session.bind)

    def test_session_closes_after_use(self) -> None:
        """Test the session is properly closed after yielding."""

        db_dependency = create_session_factory(self.test_engine)
        session_generator = db_dependency()

        with patch("sqlalchemy.orm.session.Session.close", autospec=True) as mock_close:
            with next(session_generator) as session:
                self.assertIsInstance(session, Session)

            mock_close.assert_called_once_with(session)

    async def test_async_session_is_active(self) -> None:
        """Test the generated function yields an active async session."""

        db_dependency = create_session_factory(self.test_async_engine)
        session_generator = db_dependency()

        async with await anext(session_generator) as session:
            self.assertIsInstance(session, AsyncSession)
            self.assertTrue(session.is_active)
            self.assertIs(self.test_async_engine, session.bind)

    async def test_async_session_closes_after_use(self) -> None:
        """Test the async session is properly closed after yielding."""

        db_dependency = create_session_factory(self.test_async_engine)
        session_generator = db_dependency()

        with patch("sqlalchemy.ext.asyncio.session.AsyncSession.close", autospec=True) as mock_close:
            async with await anext(session_generator) as session:
                self.assertIsInstance(session, AsyncSession)

            mock_close.assert_called_once_with(session)
