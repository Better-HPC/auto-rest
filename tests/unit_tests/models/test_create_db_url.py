from pathlib import Path
from unittest import TestCase

from auto_rest.models import create_db_url


class TestCreateDbUrl(TestCase):
    """Unit tests for the `create_db_url` function."""

    def test_create_url_with_all_params(self) -> None:
        """Verify a valid database url is returned when specifying all possible parameters."""

        driver = "postgresql"
        host = "localhost"
        port = 5432
        database = "mydb"
        username = "user"
        password = "pass"

        result = create_db_url(driver=driver, host=host, port=port, database=database, username=username, password=password)

        self.assertEqual(driver, result.drivername)
        self.assertEqual(database, result.database)
        self.assertEqual(host, result.host)
        self.assertEqual(port, result.port)
        self.assertEqual(username, result.username)
        self.assertEqual(password, result.password)

    def test_create_url_without_optional_params(self) -> None:
        """Verify a valid database url is returned when specifying only required parameters."""

        driver = "mysql"
        database = "default"

        result = create_db_url(driver=driver, database=database)

        self.assertEqual(driver, result.drivername)
        self.assertEqual(database, result.database)
        self.assertIsNone(result.host)
        self.assertIsNone(result.port)
        self.assertIsNone(result.username)
        self.assertIsNone(result.password)

    def test_create_sqlite_url_with_relative_path(self) -> None:
        """Verify SQLite URLs properly resolve relative file paths."""

        driver = "sqlite"
        path = Path("path/to/database.db")
        self.assertFalse(path.is_absolute())

        result = create_db_url(driver=driver, database=str(path))

        self.assertEqual(driver, result.drivername)
        self.assertEqual(str(path.resolve()), result.database)
        self.assertIsNone(result.host)
        self.assertIsNone(result.port)
        self.assertIsNone(result.username)
        self.assertIsNone(result.password)

    def test_create_sqlite_url_with_absolute_path(self) -> None:
        """Verify SQLite URLs properly resolve absolute file paths."""

        driver = "sqlite"
        path = Path("/absolute/path/to/database.db")
        self.assertTrue(path.is_absolute())

        result = create_db_url(driver=driver, database=str(path))

        self.assertEqual(driver, result.drivername)
        self.assertEqual(str(path), result.database)
        self.assertIsNone(result.host)
        self.assertIsNone(result.port)
        self.assertIsNone(result.username)
        self.assertIsNone(result.password)
