from pathlib import Path
from unittest import TestCase

from auto_rest.models import create_db_url


class TestCreateDbUrl(TestCase):
    """Unit tests for the `create_db_url` function."""

    def test_create_url_with_all_params(self) -> None:
        """Test creating a DB URL with all parameters provided."""

        result = create_db_url(
            driver="postgresql",
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="password"
        )

        expected_url = "postgresql://user:password@localhost:5432/test_db"
        self.assertEqual(expected_url, result)

    def test_create_url_without_password(self) -> None:
        """Test creating a DB URL without a password."""

        result = create_db_url(
            driver="postgresql",
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password=None
        )

        expected_url = "postgresql://user@localhost:5432/test_db"
        self.assertEqual(expected_url, result)

    def test_create_url_without_username_and_password(self) -> None:
        """Test creating a DB URL without a username and password."""

        result = create_db_url(
            driver="postgresql",
            host="localhost",
            port=5432,
            database="test_db",
            username=None,
            password=None
        )

        expected_url = "postgresql://localhost:5432/test_db"
        self.assertEqual(expected_url, result)

    def test_create_url_without_port(self) -> None:
        """Test creating a DB URL without a port."""

        result = create_db_url(
            driver="postgresql",
            host="localhost",
            port=None,
            database="test_db",
            username="user",
            password="password"
        )

        expected_url = "postgresql://user:password@localhost/test_db"
        self.assertEqual(expected_url, result)

    def test_create_url_without_database(self) -> None:
        """Test creating a DB URL without a database."""

        result = create_db_url(
            driver="postgresql",
            host="localhost",
            port=5432,
            database=None,
            username="user",
            password="password"
        )

        expected_url = "postgresql://user:password@localhost:5432"
        self.assertEqual(expected_url, result)

    def test_create_sqlite_url_with_relative_path(self) -> None:
        """Test SQLite URL with a relative file path."""

        path = Path("path/to/database.db")
        self.assertFalse(path.is_absolute())

        result = create_db_url(
            driver="sqlite",
            host=str(path),  # Relative path
            port=None,
            database=None,
            username=None,
            password=None
        )
        expected_url = f"sqlite:///{path.resolve()}"
        self.assertEqual(result, expected_url)

    def test_create_sqlite_url_with_absolute_path(self) -> None:
        """Test SQLite URL with an absolute file path."""

        result = create_db_url(
            driver="sqlite",
            host="/absolute/path/to/database.db",  # Absolute path
            port=None,
            database=None,
            username=None,
            password=None
        )
        expected_url = "sqlite:////absolute/path/to/database.db"
        self.assertEqual(result, expected_url)
