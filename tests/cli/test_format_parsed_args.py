import unittest
from argparse import Namespace
from gc import enable

from sqlalchemy.engine.url import URL

from auto_rest.cli import format_parsed_args


class TestFormatParsedArgs(unittest.TestCase):
    """Unit tests for the `format_parsed_args` function."""

    def test_format_parsed_args_sqlite(self):
        """Test SQLite configurations are correctly formatted."""

        args = Namespace(
            sqlite=True,
            psql=False,
            mysql=False,
            db_user=None,
            db_pass=None,
            db_host="localhost",
            db_port=None,
            db_name="test.db",
            pool_min=10,
            pool_max=50,
            pool_out=20,
            server_host="127.0.0.1",
            server_port=8000,
            log_level="INFO",
            enable_meta=True,
        )

        expected_db_url = URL.create(drivername="sqlite", host="localhost", database="test.db")
        formatted_args = format_parsed_args(args)

        self.assertEqual(formatted_args["db_url"], str(expected_db_url))
        self.assertEqual(formatted_args["pool_min"], 10)
        self.assertEqual(formatted_args["pool_max"], 50)
        self.assertEqual(formatted_args["pool_timeout"], 20)
        self.assertEqual(formatted_args["server_host"], "127.0.0.1")
        self.assertEqual(formatted_args["server_port"], 8000)
        self.assertEqual(formatted_args["log_level"], "INFO")

    def test_format_parsed_args_postgresql(self):
        """Test PostgreSQL configurations are correctly formatted."""

        args = Namespace(
            sqlite=False,
            psql=True,
            mysql=False,
            db_user="user",
            db_pass="pass",
            db_host="db.example.com",
            db_port=5432,
            db_name="mydb",
            pool_min=20,
            pool_max=100,
            pool_out=30,
            server_host="0.0.0.0",
            server_port=8080,
            log_level="DEBUG",
            enable_meta=True,
        )

        expected_db_url = URL.create(
            drivername="postgresql+asyncpg",
            username="user",
            password="pass",
            host="db.example.com",
            port=5432,
            database="mydb"
        )
        formatted_args = format_parsed_args(args)

        self.assertEqual(formatted_args["db_url"], str(expected_db_url))
        self.assertEqual(formatted_args["pool_min"], 20)
        self.assertEqual(formatted_args["pool_max"], 100)
        self.assertEqual(formatted_args["pool_timeout"], 30)
        self.assertEqual(formatted_args["server_host"], "0.0.0.0")
        self.assertEqual(formatted_args["server_port"], 8080)
        self.assertEqual(formatted_args["log_level"], "DEBUG")

    def test_format_parsed_args_mysql(self):
        """Test MySQL configurations are correctly formatted."""

        args = Namespace(
            sqlite=False,
            psql=False,
            mysql=True,
            db_user="root",
            db_pass="password",
            db_host="mysql.example.com",
            db_port=3306,
            db_name="testdb",
            pool_min=15,
            pool_max=75,
            pool_out=25,
            server_host="192.168.1.1",
            server_port=9000,
            log_level="WARNING",
            enable_meta=True,
        )

        expected_db_url = URL.create(
            drivername="mysql",
            username="root",
            password="password",
            host="mysql.example.com",
            port=3306,
            database="testdb"
        )
        formatted_args = format_parsed_args(args)

        self.assertEqual(formatted_args["db_url"], str(expected_db_url))
        self.assertEqual(formatted_args["pool_min"], 15)
        self.assertEqual(formatted_args["pool_max"], 75)
        self.assertEqual(formatted_args["pool_timeout"], 25)
        self.assertEqual(formatted_args["server_host"], "192.168.1.1")
        self.assertEqual(formatted_args["server_port"], 9000)
        self.assertEqual(formatted_args["log_level"], "WARNING")
