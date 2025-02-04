import os
from unittest import TestCase

from requests import Session as HTTPSession
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as DBSession, sessionmaker

from tests.func_tests.fixtures import FIXTURE_DATA, ModelBase

__all__ = ["FunctionTestingBase"]


class FunctionTestingBase(TestCase):
    """Base class used to set up test fixtures for API function tests."""

    _test_db = os.environ["AR_TEST_DB"]
    _test_api = os.getenv("AR_TEST_SERVER", "http://localhost:8081")

    @classmethod
    @property
    def db_url(cls) -> str:
        """Return the connection URL for the testing database."""

        return cls._test_db

    @classmethod
    @property
    def server_url(cls) -> str:
        """Return the URL for the testing API Server."""

        return cls._test_api

    @classmethod
    def setUpClass(cls) -> None:
        """Populate the database with testing fixtures."""

        # Connect to the testing database
        cls.engine = create_engine(cls.db_url)
        cls.tables = ModelBase.metadata.tables

        # Establish testing fixtures
        ModelBase.metadata.create_all(cls.engine)
        session_maker = sessionmaker(bind=cls.engine)
        with session_maker() as session:
            session.add_all(FIXTURE_DATA)
            session.commit()

    def setUp(self) -> None:
        """Instantiate a new HTTP and database sessions."""

        self.http_session = HTTPSession()
        self.db_session = DBSession(bind=self.engine)

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up the database after tests."""

        ModelBase.metadata.drop_all(cls.engine)
        cls.engine.dispose()
