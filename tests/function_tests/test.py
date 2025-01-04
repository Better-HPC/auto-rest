import multiprocessing as mp
import os
from unittest import TestCase

import requests
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

from auto_rest import run_application
from .base.fixtures import FIXTURES
from .base.schema import TestFixtureBase


class FunctionTests(TestCase):
    """Base class used to set up test fixtures for API function tests."""

    db_driver = os.getenv("AR_DB_DRIVER")
    db_port = os.getenv("AR_DB_PORT")
    db_user = os.getenv("AR_DB_USER", None)
    db_password = os.getenv("AR_DB_PASSWORD", None)
    db_host = os.getenv("AR_DB_HOST", "localhost")
    db_name = os.getenv("AR_DB_NAME", "AR_TEST")
    server_port = int(os.getenv("AR_SERVER_PORT", 8081))

    @classmethod
    def get_server_url(cls) -> str:
        """Return the API server URL."""

        return f"http://localhost:{cls.db_port}/"

    @classmethod
    def get_db_url(cls) -> URL:
        """Return the database URL."""

        if not cls.db_driver:
            raise RuntimeError("AR_DB_DRIVER environment variable not set")

        if not cls.db_port:
            raise RuntimeError("AR_DB_PORT environment variable not set")

        return URL.create(
            drivername=cls.db_driver,
            username=cls.db_user,
            password=cls.db_password,
            host=cls.db_host,
            port=int(cls.db_port),
            database=cls.db_name,
        )

    @classmethod
    def setUpClass(cls) -> None:
        """Populate the database with testing fixtures."""

        # Connect to the testing database
        cls.db_url = cls.get_db_url()
        cls.engine = create_engine(cls.db_url)

        # Establish testing fixtures
        TestFixtureBase.metadata.create_all(cls.engine)
        session_maker = sessionmaker(bind=cls.engine)
        with session_maker() as session:
            session.add_all(FIXTURES)
            session.commit()

        cls.api_server_process = mp.Process(
            target=run_application,
            args=(
                cls.db_driver,
                cls.db_host,
                cls.db_port,
                cls.db_name,
                cls.db_user,
                cls.db_password,
                cls.server_port,
            )
        )
        cls.api_server_process.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up the database after tests."""

        cls.api_server_process.kill()
        cls.api_server_process.join()

        if hasattr(cls, 'engine'):
            TestFixtureBase.metadata.drop_all(cls.engine)
            cls.engine.dispose()

    def test_api_server_running(self) -> None:
        """Test the API server is running."""

        response = requests.get(self.get_api_url())
        self.assertEqual(200, response.status_code)
