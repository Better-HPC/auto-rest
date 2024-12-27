from pathlib import Path
from unittest import TestCase

from auto_rest.models import create_db_url


class TestCreateDbUrl(TestCase):
    """Unit tests for the `create_db_url` function."""

    def test_create_url_with_all_params(self) -> None:
        """Test creating a database URL with all parameters provided."""

        driver = "postgresql"
        host = "localhost"
        port = 5432
        database = "mydb"
        username = "user"
        password = "pass"

        result = create_db_url(driver=driver, host=host, port=port, database=database, username=username, password=password)

        self.assertEqual(driver, result.drivername)
        self.assertEqual(host, result.host)
        self.assertEqual(port, result.port)
        self.assertEqual(database, result.database)
        self.assertEqual(username, result.username)
        self.assertEqual(password, result.password)

    def test_create_url_without_optional_params(self) -> None:
        """Test creating a database URL without optional parameters."""

        driver = "mysql"
        host = "127.0.0.1"

        result = create_db_url(driver=driver, host=host)

        self.assertEqual(driver, result.drivername)
        self.assertEqual(host, result.host)
        self.assertIsNone(result.port)
        self.assertIsNone(result.database)
        self.assertIsNone(result.username)
        self.assertIsNone(result.password)

    def test_create_sqlite_url_with_relative_path(self) -> None:
        """Test creating a SQLite URL with a relative file path."""

        driver = "sqlite"
        path = Path("path/to/database.db")
        self.assertFalse(path.is_absolute())

        result = create_db_url(driver=driver, host=str(path))

        self.assertEqual(driver, result.drivername)
        self.assertIsNone(result.host)
        self.assertIsNone(result.port)
        self.assertEqual(str(path.resolve()), result.database)
        self.assertIsNone(result.username)
        self.assertIsNone(result.password)

    def test_create_sqlite_url_with_absolute_path(self) -> None:
        """Test creating a SQLite URL with an absolute file path."""

        driver = "sqlite"
        path = Path("/absolute/path/to/database.db")
        self.assertTrue(path.is_absolute())

        result = create_db_url(driver=driver, host=str(path))

        self.assertEqual(driver, result.drivername)
        self.assertIsNone(result.host)
        self.assertIsNone(result.port)
        self.assertEqual(str(path), result.database)
        self.assertIsNone(result.username)
        self.assertIsNone(result.password)
