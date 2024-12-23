import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from auto_rest.dependencies import create_db_dependency


class TestCreateDbDependency(unittest.TestCase):
    """Unit tests for the `create_db_dependency` function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up a test database engine."""

        cls.test_engine: Engine = create_engine("sqlite:///:memory:")

    def test_dependency_returns_active_session(self) -> None:
        """Test the generated dependency yields an active session."""

        db_dependency = create_db_dependency(self.test_engine)
        session_generator = db_dependency()

        with next(session_generator) as session:
            self.assertIsInstance(session, Session)
            self.assertTrue(session.is_active)
            self.assertIs(self.test_engine, session.bind)

    def test_session_closes_after_use(self) -> None:
        """Test the session is properly closed after yielding."""

        db_dependency = create_db_dependency(self.test_engine)
        session_generator = db_dependency()

        with patch("sqlalchemy.orm.session.Session.close", autospec=True) as mock_close:
            with next(session_generator) as session:
                self.assertIsInstance(session, Session)

            mock_close.assert_called_once_with(session)
