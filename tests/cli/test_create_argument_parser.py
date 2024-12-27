from argparse import ArgumentError, ArgumentParser
from unittest import TestCase

from auto_rest.cli import create_argument_parser


class TestCreateArgumentParser(TestCase):
    """Unit tests for the `create_argument_parser` function."""

    def setUp(self) -> None:
        """Set up a new parser instance for each test."""

        self.parser = create_argument_parser(exit_on_error=False)

    def test_parser_name(self) -> None:
        """Test the parser is created with the correct program name."""

        self.assertIsInstance(self.parser, ArgumentParser)
        self.assertEqual("auto-rest", self.parser.prog)

    def test_log_level(self) -> None:
        """Test only valid log levels are accepted and default value is correct."""

        # Validate the default log level
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertEqual("INFO", args.log_level)

        # Test valid logging levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        for level in valid_levels:
            args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--log-level", level])
            self.assertEqual(level, args.log_level)

        # Test an invalid logging level
        with self.assertRaises(ArgumentError):
            self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--log-level", "INVALID"])

    def test_db_driver_selection(self) -> None:
        """Test mutually exclusive arguments for database driver selection."""

        # Test valid database driver options
        cli_flags = ["sqlite", "psql", "mysql", "oracle", "mssql"]
        db_drivers = ["sqlite", "postgresql+asyncpg", "mysql+asyncmy", "oracle+oracledb", "mssql+aiomysql"]

        for flag, driver in zip(cli_flags, db_drivers):
            args = self.parser.parse_args([f"--{flag}", "--db-host", "localhost"])
            self.assertEqual(driver, args.db_driver)

        # Test custom driver
        args = self.parser.parse_args(["--driver", "custom-driver", "--db-host", "localhost"])
        self.assertEqual("custom-driver", args.db_driver)

    def test_db_settings(self) -> None:
        """Test database-related arguments and default values."""

        # Test required database host
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertEqual("localhost", args.db_host)

        # Test default database port
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertEqual(None, args.db_port)

        # Test optional db-name, user, and password
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--db-name", "testdb", "--db-user", "user", "--db-pass", "password"])
        self.assertEqual("testdb", args.db_name)
        self.assertEqual("user", args.db_user)
        self.assertEqual("password", args.db_pass)

    def test_pool_settings(self) -> None:
        """Test database connection pool settings and defaults."""

        # Test default pool settings (None should be default)
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertIsNone(args.pool_min)
        self.assertIsNone(args.pool_max)
        self.assertIsNone(args.pool_out)

        # Test valid pool settings
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--pool-min", "5", "--pool-max", "20", "--pool-out", "30"])
        self.assertEqual(5, args.pool_min)
        self.assertEqual(20, args.pool_max)
        self.assertEqual(30, args.pool_out)

    def test_enabled_docs_flag(self) -> None:
        """Test the `--enable-docs` flag behavior."""

        # Default should be False
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertFalse(args.enable_docs)

        # Test enabling docs
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--enable-docs"])
        self.assertTrue(args.enable_docs)

    def test_enabled_meta_flag(self) -> None:
        """Test the `--enable-meta` flag behavior."""

        # Default should be False
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertFalse(args.enable_meta)

        # Test enabling meta
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--enable-meta"])
        self.assertTrue(args.enable_meta)

    def test_server_settings(self) -> None:
        """Test server related settings and default values."""

        # Test default server host and port
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost"])
        self.assertEqual("127.0.0.1", args.server_host)
        self.assertEqual(8081, args.server_port)

        # Test custom server host and port
        args = self.parser.parse_args(["--sqlite", "--db-host", "localhost", "--server-host", "0.0.0.0", "--server-port", "9090"])
        self.assertEqual("0.0.0.0", args.server_host)
        self.assertEqual(9090, args.server_port)
